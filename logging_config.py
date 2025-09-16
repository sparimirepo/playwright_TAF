import logging
import sys
import os


def setup_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] '
                                      '[%(filename)s:%(lineno)d] - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S'
                                      )

        # Create logs  folder if it doesn't exit
        os.makedirs('logs', exist_ok=True)

        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        # File Handler
        fh = logging.FileHandler('logs/test_run.log', mode='a', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


global_logger = setup_logger('NextGen_Test_Framework')
