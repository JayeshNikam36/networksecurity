from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import pandas as pd
import numpy as np

#configuration for data ingestion
from networksecurity.entity.config_entity import TrainingPipelineConfig, DataIngetionConfig
import os
import sys
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
from networksecurity.entity.artifact_entity import DataIngestionArtifact
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngetionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_collection_as_dataframe(self):
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]
            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], axis=1, inplace=True)
            df.replace({"na":np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def export_data_to_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame) -> List[pd.DataFrame]:
        try:
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio, random_state=42)
            logging.info(f"Train set shape: {train_set.shape}, Test set shape: {test_set.shape}")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Train file path: {self.data_ingestion_config.training_file_path}")
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            logging.info(f"Test file path: {self.data_ingestion_config.testing_file_path}")
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
            logging.info("Data ingestion completed successfully.")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

        
    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_to_feature_store(dataframe=dataframe)
            self.split_data_as_train_test(dataframe=dataframe)
            dataingestionartifact = DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                          test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)