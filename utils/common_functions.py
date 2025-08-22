import os 
import pandas
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found in the given path : {file_path}")
        with open (file_path,"r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info(f"YAML file loaded successfully from {file_path}")
            return config
    except Exception as e:
        logger.error(f"Error while reading YAML file")
        raise CustomException(f"Error while reading YAML file",e)
    
def load_data(path):
    try:
        logger.info("Loading Data")
        return pandas.read_csv(path)
    except Exception as e:
        logger.error(f'Error while loading data,{e}')
        raise CustomException(f'Failed to load data from {path}', e)
    