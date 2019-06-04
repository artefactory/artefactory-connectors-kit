import logging
import os


FORMAT = '%(asctime)s - (%(name)s) - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def env():
    return os.environ.get('ENV', 'dev')


def is_staging():
    return env() == 'staging'


def is_dev():
    return env() == 'dev'


def is_production():
    return env() == 'production'


for key, var in os.environ.iteritems():
    locals()[key] = var
