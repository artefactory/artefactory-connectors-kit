import os


def env():
    return os.environ.get('ENV', 'dev')


def is_staging():
    return env() == 'staging'


def is_dev():
    return env() == 'dev'


def is_production():
    return env() == 'production'
