from ipvanish import change_ip
import sys

import logging, sys
# logging
# logging, I know this is comple BS code , but google could not help me
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)-8s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def docker_runner():
    while True:
        try:
            change_ip()
        except KeyboardInterrupt:
            logger.info('keyboard interrupt')
            sys.exit(0)
        except Exception as e:
            logger.exception(e)

if __name__ == "__main__":
    docker_runner()