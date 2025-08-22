import os
import pandas as pd
from sklearn.model_selection import train_test_split
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.common_functions import read_yaml
from config.paths_config import *

logger= get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]  # read data_ingestion config from config.yaml
        self.bucket_name = self.config["bucket_name"] # for data_ingestion we created self.config. indise it bucket_name
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR,exist_ok=True)

        logger.info(f"Data Ingestion initialized with {self.bucket_name} and  file name {self.bucket_file_name}")

    def dowload_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)  # blob means file name
            
            blob.download_to_filename(RAW_FILE_PATH)  # download to local path

            logger.info(f"File {self.file_name} downloaded from GCS bucket {self.bucket_name} to {RAW_FILE_PATH}")
        
        except Exception as e:
            logger.error("Error while downloading file from GCS")
            raise CustomException("Failed to dowload the csv file", e) 
        
    def split_data(self):
        try:
            logger.info("Splitting data into train and test sets")
            data = pd.read_csv(RAW_FILE_PATH)

            train_data,test_data = train_test_split(data,train_size=self.train_test_ratio, random_state=42)


            # convert to csv
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)

            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")

        except Exception as e:
            logger.error("Error while splitting data into train and test sets")
            raise CustomException("Failed to split the data", e)

    def run(self):
        try:
            logger.info("Starting data ingestion process")
            self.dowload_csv_from_gcp()
            self.split_data()
            logger.info("Data ingestion process completed successfully")
        except Exception as e:
            logger.error(f"CustomException: {str(e)}")


        finally:
            logger.info("Data ingestion completed")    

if __name__=="__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()
    
                