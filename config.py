import logging
import os

import env

FORMAT = '%(asctime)s - (%(name)s) - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ENV = env.env()

BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))
ENVIRONMENT = os.path.join(BASE_PATH, 'environments', ENV)


def read_bash_variables(path):
    config_vars = {}
    with open(path, 'r') as f:
        for line in f:
            if '=' in line:
                k, v = line.replace('\n', '').split('=', 1)
                config_vars[k] = v
    return config_vars


config = read_bash_variables(ENVIRONMENT)
