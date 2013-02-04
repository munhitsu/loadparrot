"""
Model of Test Scenario

Scenario is configured using
- list of UserAgent(s)
- load speeds
- list of UserSession(s)

UserSession is a list of class based on UserSessionStep:
- Request
- ThinkTime
...


note about probability
~~~~~~~~~~~~~~~~~~~~~~

As some objects are configured with probability you may expect to see objects
distributed exactly as specified.

What it in fact means is that on each event, with probability specified, random
function is executed. So say we have UserAgent(ie6, probablity=90) and
UserAgent(safari6, probability=10). Each time we need to select UserAgent we
toss a 10 side "dice".

So we have 10% probability to reach safari and 90% probability to get ie6.
Throwing the dice 100 times we will get _close_ to 10 of safari and close to
90 of _ie6_.

"""

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from geventhttpclient.client import Header
import time
import random
import copy
from loadparrot.utils import WeightedRandomGenerator

import logging
log = logging.getLogger(__name__)


class ScenarioError(Exception):
    pass


#TODO: implement requests_limit
class UserAgent(object):
    """
    configures UserSession
    """

    SAFARI_6 = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"
    FIREFOX_18 = "Mozilla/5.0 (Windows NT 5.1; rv:18.0) Gecko/20100101 Firefox/18.0"
    IE_10_6 = "Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0"
    CHROME_24 = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"

    def __init__(self, name, agent_string, probability=100, requests_limit=1):
        """
        :param name: i.e. UserAgent.SAFARI_6
        :param probability: what is the probability of this agent being used on
        UserSession
        :param requests_limit: how many requests can be executed in parallel
        """
        self.name = name
        self.agent_string = agent_string
        self.probability = probability
        self.requests_limit = requests_limit

    def __repr__(self):
        return __str__()

    def __str__(self):
        return self.name

    def get_as_dict(self):
        """
        a representation for geventhttpclient
        """
        return {
            'User-Agent': self.agent_string
        }


class UserSession(list):
    """
    Object that is send to worker to execute
    """

    def __init__(self, name, probability=100):
        super(UserSession, self).__init__()
        self.name = name
        self.probability = probability

    def __call__(self, *args, **kwargs):
        log.debug("Executing UserSession {name} using agent {agent}".format(name=self.name,agent=self.runtime_config["agent"]))
        start = time.time()
        step_start = finish = start
        times_for_steps = []
        for step in self:
            assert isinstance(step, UserSessionStep)
            step()
            finish = time.time()
            step_duration = finish - step_start
            times_for_steps.append((step.__str__(), step_duration))
            step_start = finish
        session_duration = finish - start
        return {
            'duration': session_duration,
            'steps': times_for_steps,
        }

    def get_configured(self, runtime_config):
        """
        Performs a deep copy of self and configures all session steps
        with runtime_config
        Such session can be send to worker

        :param runtime_config: runtime_configuration
        :type runtime_config: RuntimeConfig
        :rtype: UserSession
        """
        session = copy.deepcopy(self)
        for session_step in session:
            assert isinstance(session_step, UserSessionStep)
            session_step.runtime_config = runtime_config

        session.runtime_config = runtime_config
        return session


class UserSessionStep(object):
    """
    An abstract step. Inherit and implement __init__ and __call__
    """

    runtime_config = None  # it will be initialized by UserSession on send

    def __call__(self, *args, **kwargs):
        assert self.runtime_config
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()


#TODO: add sending bunch of requests at once (agent requests_limit)
class Request(UserSessionStep):
    """
    SessionStep that performs simple http request.
    """

    def __init__(self, url, version="1.1", method="GET"):
        self.url = url
        self.url_object = URL(url)
        self.version = version
        self.method = method

    def __str__(self):
        return "{method} {url}".format(**self.__dict__)

    def __call__(self, *args, **kwargs):
        assert self.runtime_config
        url = self.url_object
        http = HTTPClient(url.host, headers=self.runtime_config["agent"].get_as_dict())
        response = http.get(url.path)
        code = response.status_code
        log.debug("%s %s", self.url, code)
        body = response.read()
        http.close()


class ThinkTime(UserSessionStep):
    """
    SessionStep that simulates user pause between requests.
    """

    def __init__(self, random=True, value=1):
        self.random = random
        self.value = value

    def __str__(self):
        if self.random:
            return "sleep(random({0}))".format(self.value)
        else:
            return "sleep({0})".format(self.value)

    def __call__(self, *args, **kwargs):
        assert self.runtime_config
        duration = random.random() * self.value if self.random else self.value
        time.sleep(duration)

class RuntimeConfig(dict):
    """
    dictionary wrapper so that config passed to workers is more readable
    """

    def __init__(self, agent):
        super(RuntimeConfig, self).__init__()
        self["agent"] = agent


class Scenario(list):
    """
    Returns UserSessions based on configuration
    """

    def __init__(self, name, user_agents, load, user_sessions):
        """
        :param name: name of scenario
        :param user_agents: list of UserAgent objects
        :param load: definition of load
        :type load: list of tuples of

        """
        super(Scenario, self).__init__()
        # validating agents
        probability = 0
        for agent in user_agents:
            assert isinstance(agent, UserAgent)
            probability += agent.probability
        if probability != 100:
            raise ScenarioError("Agent probability sum = {probability}".
                                format(probability=probability))

        # validating sessions
        probability = 0
        for session in user_sessions:
            assert isinstance(session, UserSession)
            probability += session.probability
        if probability != 100:
            raise ScenarioError("UserSession probability sum = {probability}".
                                format(probability=probability))

        self.name = name
        self.user_agents = user_agents
        self.load = load
        self.user_sessions = user_sessions

    def __call__(self, *args, **kwargs):
        """
        executes all user_sessions
        """

        for user_session in self:
            assert isinstance(user_session, UserSession)
            user_session()

    def get_user_session(self):
        """
        yelds return UserSession objects
        objects are configured based on Scenario specification
        """
        #let's initialize random generators
        agent_random = WeightedRandomGenerator(
            map(lambda x: x.probability, self.user_agents))
        user_session_random = WeightedRandomGenerator(
            map(lambda x: x.probability, self.user_sessions))

        while True:
            s_agent = self.user_agents[agent_random()]
            s_user_session = self.user_sessions[user_session_random()]
            runtime_config = RuntimeConfig(agent=s_agent)
            c_user_session = s_user_session.get_configured(runtime_config=runtime_config)
            yield c_user_session
