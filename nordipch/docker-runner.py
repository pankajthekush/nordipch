from ipvanish import change_ip
from ilogger import logger
import sys

def docker_runner():
    while True:
        try:
            change_ip()
        except KeyboardInterrupt:
            logger.info('keyboard interrupt')
            sys.exit(0)
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    docker_runner()