from gevent.monkey import patch_all
patch_all()

import zmq.green as zmq
import time
import loadparrot.utils

from loadparrot.model import MessageAction
import config

import logging
log = logging.getLogger(__name__)


def main():
    context = zmq.Context()

    task_socket = context.socket(zmq.PULL)
    task_socket.connect("tcp://127.0.0.1:{0}".format(config.TASK_PORT))

    stat_socket = context.socket(zmq.PUSH)
    stat_socket.connect("tcp://127.0.0.1:{0}".format(config.STAT_PORT))

    fan_socket = context.socket(zmq.SUB)
    fan_socket.connect("tcp://127.0.0.1:{0}".format(config.FANOUT_PORT))
    fan_socket.setsockopt(zmq.SUBSCRIBE, "")


    poller = zmq.Poller()
    poller.register(task_socket, zmq.POLLIN)
    poller.register(fan_socket, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())
        if fan_socket in socks and socks[fan_socket] == zmq.POLLIN:
            message = fan_socket.recv_pyobj()
            log.debug(message)
            if message.content == MessageAction.EXIT:
                print message
                break
            else:
                raise Exception("Unsupported Message: {1}".format(message))
        elif task_socket in socks and socks[task_socket] == zmq.POLLIN:
            scenario = task_socket.recv_pyobj()
            log.debug(scenario)
            stats = scenario()
            stat_socket.send_pyobj(stats)

    # time to close
    poller.unregister(task_socket)
    poller.unregister(fan_socket)

if __name__ == "__main__":
    main()
