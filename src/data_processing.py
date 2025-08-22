import os
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.common_functions import read_yaml,load_data
from config.paths_config import *
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

logger=get_logger(__name__)

class DataProcessor:
    def __init__(self, train_path, test_path,processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir

        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
            logger.info(f"Processed directory created at {self.processed_dir}")

    def preprocess_data(self,df):

        try:
            logger.info("starting the data processing steps")

            logger.info("Dropping the columns")
            df.drop(columns=['Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols= self.config["data_processing"]["categorical_columns"]
            num_cols= self.config["data_processing"]["numerical_columns"]

            logger.info("applying LabelEncoding")

            label_encoder = LabelEncoder()
            mapping={}
            for col in cat_cols:
                df[col]=label_encoder.fit_transform(df[col])
                mapping[col]={label:code for label,code in zip(label_encoder.classes_,label_encoder.transform(label_encoder.classes_))}
            logger.info("Label Encoding completed") 
            logger.info("Label Mappings are:")
            for col, mapping in mapping.items():
                logger.info(f"{col}: {mapping}")

            logger.info("Doing skewness treatment")
            skew_threshold= self.config["data_processing"]["skewness_threshold"]
            skewness = df[num_cols].apply(lambda x:x.skew())

            for column in skewness[skewness>skew_threshold].index:
                df[column] = np.log1p(df[column])

            return df
        except Exception as e:
            logger.error(f"Error in data preprocessing: {e}")
            raise CustomException(f"Data preprocessing failed", e)
        
    def balance_data(self,df):
        try:
            logger.info("Handling imbalanceed data")
            x=df.drop(columns=['booking_status'])
            y=df['booking_status']
            smote=SMOTE(random_state=42)
            x_resampled,y_resampled=smote.fit_resample(x,y)

            balanced_df=pd.DataFrame(x_resampled,columns=x.columns)
            balanced_df['booking_status'] = y_resampled

            logger.info("data balancing completed")

            return balanced_df
        except Exception as e:
            logger.error(f"Error in balancing data: {e}")
            raise CustomException(f"Data balancing failed", e)
        
    def select_featurees(self,df):
        try:
            logger.info("Selecting features using Random Forest Classifier")

            x=df.drop(columns=['booking_status'])
            y=df['booking_status']   

            model=RandomForestClassifier(random_state=15)
            model.fit(x,y)
            feature_importance=model.feature_importances_
            feature_importance_df=pd.DataFrame({
                    'feature': x.columns,
                    'importance' : feature_importance
                        })
            
            top_feature_importance_df=feature_importance_df.sort_values(by='importance', ascending=False)

            num_features_to_select = self.config['data_processing']['no_of_features']
            selected_features=top_feature_importance_df['feature'].head(num_features_to_select).values

            logger.info(f"Selected top {num_features_to_select} features: {selected_features}")

            top_feature_df=df[selected_features.tolist()+['booking_status']] 
            logger.info("Feature selection completed")

            return top_feature_df
        
        except Exception as e:
            logger.error(f"Error in feature selection: {e}")
            raise CustomException(f"Feature selection failed", e)
        
    def save_data(self,df,file_path):
        try:
            logger.info(f"Saving processed data to {file_path}")
            df.to_csv(file_path,index=False)
            logger.info("Data saved successfully")

        except Exception as e:
            logger.error(f"Error in saving data: {e}")
            raise CustomException(f"Data saving failed", e)

    def process(self):
        try:
            logger.info("Starting data processing")
            
            train_df= load_data(self.train_path)
            test_df= load_data(self.test_path)
            logger.info("Data loaded successfully")

            train_df =self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)
            logger.info("Data preprocessing completed")

            train_df = self.balance_data(train_df)
            test_df = self.balance_data(test_df)
            logger.info("Data balancing completed")

            train_df = self.select_featurees(train_df)
            test_df = test_df[train_df.columns] #select features not used as test data may have diffrent set of features as required by the model
            logger.info("Feature selection completed")

            self.save_data(train_df, PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH)
            logger.info("Data processing completed successfully")

        except Exception as e:
            logger.error(f"Error in data processing pipeline : {e}")
            raise CustomException(f"Data processing failed", e)
        
# to check the data processing pipeline
if __name__ == "__main__": # to run the script directly 
    processor = DataProcessor(TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_DIR, CONFIG_PATH)   
    processor.process() # call the process function to start the data processing pipeline     
            




    