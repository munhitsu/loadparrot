"""
temporary way to create scenario
"""

from loadparrot.model import *


def get_scenario():
    """
    overwrite with your scenario
    """
    agents = [
        UserAgent(name="ie10", agent_string=UserAgent.IE_10_6, probability=40, requests_limit=1),
        UserAgent(name="safari6", agent_string=UserAgent.SAFARI_6, probability=20, requests_limit=1),
        UserAgent(name="chrome", agent_string=UserAgent.CHROME_24, probability=40, requests_limit=1),
    ]

    # incoming users speeds (duration in seconds, new users per second),...
    load = [(5, 10), (1, 100), (10, 0), (5, -10)]

    sessionA = UserSession(name="primary", probability=30)
    sessionA.append(Request(url="http://google.com/"))
    sessionA.append(ThinkTime(value=1))
    sessionA.append(Request(url="http://www.google.com/services/"))

    sessionB = UserSession(name="secondary", probability=70)
    sessionB.append(Request(url="http://google.com/"))
    sessionB.append(ThinkTime(value=1, random=True))
    sessionB.append(Request(url="http://www.google.co.uk/#output=search&q=foo"))
    sessions = [sessionA, sessionB]

    s = Scenario(name="test-0.0.1", user_agents=agents, load=load, user_sessions=sessions)
    return s


scenario = get_scenario()
