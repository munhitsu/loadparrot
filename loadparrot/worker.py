"""
worker to run on each host
execute::

    python loadparrot/worker.py -h

"""

from gevent.monkey import patch_all
patch_all()

import zmq.green as zmq

from loadparrot.messages import MessageAction
import loadparrot.utils
import config
import logging
log = logging.getLogger(__name__)


import argparse


def run_worker():
    """
    Main loop. Worker is fully managed by master.
    """
    log.info("Connecting to KING: {ip}".format(ip=config.KING_IP))
    context = zmq.Context()

    task_socket = context.socket(zmq.PULL)
    task_socket.connect("tcp://{ip}:{port}".format(ip=config.KING_IP, port=config.TASK_PORT))

    stat_socket = context.socket(zmq.PUSH)
    stat_socket.connect("tcp://{ip}:{port}".format(ip=config.KING_IP, port=config.STAT_PORT))

    fan_socket = context.socket(zmq.SUB)
    fan_socket.connect("tcp://{ip}:{port}".format(ip=config.KING_IP, port=config.FANOUT_PORT))
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
            user_session = task_socket.recv_pyobj()
            log.debug(user_session)
            stats = user_session()
            stat_socket.send_pyobj(stats)

    # time to close
    poller.unregister(task_socket)
    poller.unregister(fan_socket)


def main():
    """
    Parses arguments and calls :func:`run_worker`
    """
    parser = argparse.ArgumentParser(description="Let's make some load")
    parser.add_argument("--king",
                        help="King address IP",
                        default=config.KING_IP)
    args = parser.parse_args()
    config.KING_IP = args.king
    run_worker()

if __name__ == "__main__":
    main()
