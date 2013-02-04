"""
Messages passed between master and workers
"""

import logging
log = logging.getLogger(__name__)


class MessageAction(object):
    """
    Message requesting specific action
    """
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
