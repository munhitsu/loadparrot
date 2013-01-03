TASK_PORT = 4444
STAT_PORT = 4445
FANOUT_PORT = 4446

import logging
ch = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
