import logging


FORMAT = '%(asctime)s - (%(name)s) - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
