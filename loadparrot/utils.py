"""
Various utilities
"""

import zmq
import random
import bisect

print "Current 0MQ version is " + zmq.zmq_version()


class WeightedRandomGenerator(object):
    """
    Best weighted random generator not requiring numpy
    Source:
    http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python
    """
    def __init__(self, weights):
        self.totals = []
        running_total = 0

        for w in weights:
            running_total += w
            self.totals.append(running_total)

    def next(self):
        rnd = random.random() * self.totals[-1]
        return bisect.bisect_right(self.totals, rnd)

    def __call__(self):
        return self.next()
