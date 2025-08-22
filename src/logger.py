import logging
import os
from datetime import datetime

# to make logs directory if it doesn't exist
logs_dir = 'logs'
os.makedirs(logs_dir, exist_ok=True)

LOG_FILE = os.path.join(logs_dir,f"log_{datetime.now().strftime('%Y-%M-%d')}.log")

#set up logging configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,  # 3 types of info- formal, warning and error
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

