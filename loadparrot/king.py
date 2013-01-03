from gevent.monkey import patch_all
patch_all()

import zmq.green as zmq
import time
import loadparrot.utils
import sys

from loadparrot.model import get_user_session, MessageAction
from loadparrot import config


# incoming users speeds (duration in seconds, new users per second)
session_one_speeds = [(5, 10), (1, 100), (10, 0), (5, -10)]


class ClosingException(Exception):
    pass

#TODO: optimize (cache pre-calculated data)
def users_since_t0(t0, t_now, speeds):
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
    context = zmq.Context()

    # task distribution
    task_socket = context.socket(zmq.PUSH)
    task_socket.bind("tcp://127.0.0.1:{0}".format(config.TASK_PORT))

    # returned statistics
    stat_socket = context.socket(zmq.PULL)
    stat_socket.bind("tcp://127.0.0.1:{0}".format(config.STAT_PORT))

    # fanout communication channel
    fanout_socket = context.socket(zmq.PUB)
    fanout_socket.bind("tcp://127.0.0.1:{0}".format(config.FANOUT_PORT))

    poller = zmq.Poller()
    poller.register(stat_socket, zmq.POLLIN)

    user_session = get_user_session()

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
            expected_users = users_since_t0(t0, t_now, session_one_speeds)
            users_delta = expected_users - current_users
            if users_delta > 0:
                for user in xrange(users_delta):
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
#    fanout_socket.send_pyobj(MessageAction(MessageAction.EXIT))

    #TODO add timeout calculated from scenarios
    #TODO: move to separate process
    while current_users:
        stat = stat_socket.recv_pyobj()
        consume_stats(stat)
        current_users -= 1
        print "closing - remaining current_users: {0}".format(current_users)

    poller.unregister(stat_socket)

if __name__ == "__main__":
    main()
