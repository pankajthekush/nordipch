from nordipch import change_ip
from ilogger import logger
import sys


"""
    Docker runner for nord
"""
def docker_runner():
    while True:
        try:
            change_ip()
        except KeyboardInterrupt:
            logger.info('keyboard interrupt')
            sys.exit(0)
        except Exception as e:
            print(e)
            pass

if __name__ == "__main__":
    docker_runner()
    print('runner exited')