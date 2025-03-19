import logging

logger = logging.getLogger(__name__)
FORMAT = "%(asctime)s - %(message)s"
logging.basicConfig(format=FORMAT)
logger.addHandler(logging.FileHandler("gamelog.log"))
logger.setLevel(logging.DEBUG)
