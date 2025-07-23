from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataIngetionConfig, DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from scipy.stats import ks_2samp
import pandas as pd
import os
import sys
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_util.utils import write_yaml_file
from networksecurity.utils.main_util.utils import read_yaml_file

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_dataframe(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_columns = self._schema_config['columns']
            number_of_columns = len(expected_columns)
            logging.info(f"Expected number of columns: {number_of_columns}, Actual number of columns: {len(dataframe.columns)}")
            logging.info(f"Dataframe columns: {list(dataframe.columns)}")
            logging.info(f"Expected columns from schema: {[list(col.keys())[0] for col in expected_columns]}")

            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def detect_data_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_sample_dist = ks_2samp(d1, d2)
                if threshold <= is_sample_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report.update({column: {
                    "p_value": is_sample_dist.pvalue,
                    "drift_status": is_found
                }})
            dir_path = os.path.dirname(self.data_validation_config.drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            print("Saving drift report to:", self.data_validation_config.drift_report_file_path)
            write_yaml_file(file_path = self.data_validation_config.drift_report_file_path, content=report)
            logging.info(f"Drift report written to: {self.data_validation_config.drift_report_file_path}")
            return status 
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logging.info("Starting data validation process...")
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            train_dataframe = DataValidation.read_dataframe(train_file_path)
            test_dataframe = DataValidation.read_dataframe(test_file_path)
            logging.info("Data validation completed successfully.")
            status = self.validate_number_of_columns(train_dataframe)
            if not status:
                raise NetworkSecurityException("Number of columns in the train data does not match the schema.", sys)
            status = self.validate_number_of_columns(test_dataframe)
            if not status:
                raise NetworkSecurityException("Number of columns in the test data does not match the schema.", sys)
            status = self.detect_data_drift(base_df=train_dataframe, current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)
            
            data_validation_artifact = DataValidationArtifact(
            validation_status=status,
            valid_train_file_path=self.data_validation_config.valid_train_file_path,
            valid_test_file_path=self.data_validation_config.valid_test_file_path,
            invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
            invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
            drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            
            logging.info(f"Data validation artifact created: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)


