"""
Master of puppets

Initializes Scenario and distributes to all workers specific UserSessions.

We send user session to worker and wait for response.
Knowing how many sessions we've send and responses received we know how many
sessions are open at the moment. We constantly monitor how many sessions are
needed according to scenario load and send them to workers.

"""

from gevent.monkey import patch_all
patch_all()

import zmq.green as zmq
import time
import loadparrot.utils
import sys

from loadparrot.scenario import scenario
from loadparrot.messages import MessageAction
import loadparrot.utils
import config
import logging
log = logging.getLogger(__name__)





class ClosingException(Exception):
    """
    Throw to finish running
    """
    pass


def users_since_t0(t0, t_now=time.time, speeds=()):
    """
    Number of expected users logged on server at t_now

    :param t0: start of load - our day 0
    :param t_now: give time.time()
    :param speeds: array of tuples (durations in second, new users per second)
    :type speeds: []
    :rtype: int - number of expected users
    :raises: ClosingException - if no more users programmed in speeds array
    """
    #TODO: optimize (cache pre-calculated data)
    t_delta = t_now - t0
    combined_users = 0
    combined_time = 0
    for (duration, speed) in speeds:
        if t_delta > (combined_time + duration):
            combined_time += duration
            combined_users += duration * speed
        else:
            sub_duration = t_delta - combined_time
            combined_users += sub_duration * speed
            return int(combined_users)

    # if we are out of speeds than time pull the handbrake
    raise ClosingException


def main():
    """
    runner
    """

    context = zmq.Context()

    # task distribution
    task_socket = context.socket(zmq.PUSH)
    task_socket.bind("tcp://0.0.0.0:{0}".format(config.TASK_PORT))

    # returned statistics
    stat_socket = context.socket(zmq.PULL)
    stat_socket.bind("tcp://0.0.0.0:{0}".format(config.STAT_PORT))

    # fanout communication channel
    fanout_socket = context.socket(zmq.PUB)
    fanout_socket.bind("tcp://0.0.0.0:{0}".format(config.FANOUT_PORT))

    poller = zmq.Poller()
    poller.register(stat_socket, zmq.POLLIN)

    user_session_generator = scenario.get_user_session()

    t0 = time.time()
    t_now = t0
    current_users = 0

    def consume_stats(stat):
        print stat

    # flush results queue
    while True:
        socks = dict(poller.poll(timeout=0))
        if stat_socket in socks and socks[stat_socket] == zmq.POLLIN:
            stat = stat_socket.recv_pyobj()
            print ",",
        else:
            break

    running = True

    while running:
        try:
            # balancing amount of user sessions
            expected_users = users_since_t0(t0, t_now, scenario.load)
            users_delta = expected_users - current_users
            if users_delta > 0:
                for user in xrange(users_delta):
                    user_session = user_session_generator.next()
                    assert user_session is not None
                    task_socket.send_pyobj(user_session)
                    sys.stdout.write('.')
                    sys.stdout.flush()
                current_users += users_delta
        except ClosingException:
            running = False

        time.sleep(0.1)

        # let's pick up all stats
        #TODO: move to separate process
        while True:
            socks = dict(poller.poll(timeout=0))
            if stat_socket in socks and socks[stat_socket] == zmq.POLLIN:
                stat = stat_socket.recv_pyobj()
                consume_stats(stat)
                current_users -= 1
                print "running - remaining current_users: {0}".format(current_users)
            else:
                break
        t_now = time.time()
    if config.EXIT_WORKERS:
        fanout_socket.send_pyobj(MessageAction(MessageAction.EXIT))

    #TODO: add timeout calculated from scenarios
    #TODO: move to separate process
    while current_users:
        stat = stat_socket.recv_pyobj()
        consume_stats(stat)
        current_users -= 1
        print "closing - remaining current_users: {0}".format(current_users)

    poller.unregister(stat_socket)


if __name__ == "__main__":
    main()
