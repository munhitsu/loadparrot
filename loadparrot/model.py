from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

import time
import random

import logging
log = logging.getLogger(__name__)


class UserAgent:
    SAFARI_6 = " Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.8) Gecko/20050513 Galeon/1.3.21"

    def __init__(self, name, probability=100):
        """
        i.e. Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.8) Gecko/20050513 Galeon/1.3.21
        """
        pass


class Scenario(list):
    def __init__(self, name):
        super(Scenario,self).__init__()
        self.name = name

    def __call__(self, *args, **kwargs):
        for session in self:
            session()


class Session(list):
    def __init__(self, name, probability=100, user_agents=[]):
        super(Session,self).__init__()
        self.name = name

    def __call__(self, *args, **kwargs):
        start = time.clock()
        for step in self:
            step()
        finish = time.clock()
        return {'duration': finish - start}


class SessionStep:

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


    def __repr__(self):
        return self.__str__()

class Request(SessionStep):
    def __init__(self, url, version="1.1", method="GET"):
#        super(Request, self).__init__()
        self.url = url
        self.url_object = URL(url)
        self.version = version
        self.method = method

    def __str__(self):
        return "{method} {url}".format(**self.__dict__)

    def __call__(self, *args, **kwargs):
        log.debug(self.url)

    def __call_2__(self, *args, **kwargs):
        url = self.url_object
        http = HTTPClient(url.host)
        response = http.get(url.path)
        code = response.status_code
        log.debug("%s %s", self.url, code)
        body = response.read()
        http.close()


class ThinkTime(SessionStep):
    def __init__(self, random=True, value=1):
#        super(ThinkTime, self).__init__()
        self.random = random
        self.value = value

    def __str__(self):
        if self.random:
            return "sleep(random({0}))".format(self.value)
        else:
            return "sleep({0})".format(self.value)

    def __call__(self, *args, **kwargs):
        duration = random.random() * self.value if self.random else self.value
        time.sleep(duration)

class MessageAction:
    EXIT = 1
    HANDBRAKE = 2
    verbose = {
        EXIT:      "Remote EXIT request",
        HANDBRAKE: "Remote HANDBRAKE request"
    }

    def __init__(self, action, content=None):
        self.action = action
        self.content = content

    def __str__(self):
        return "{0}: {1}".format(self.verbose[self.action], self.content)



def get_scenario():
    pass

def get_user_session():
    session = Session(name="primary")
    session.append(Request(url="http://localhost:8080"))
    session.append(ThinkTime(value=1))
    session.append(Request(url="http://localhost:8080/"))
    return session
