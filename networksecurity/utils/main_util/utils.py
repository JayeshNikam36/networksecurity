import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os
import sys
import numpy as np
import dill
import pickle

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'rb') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        if replace and os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'w') as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def save_numpy_array_data(file_path:  str, array: np.array) -> None:
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file:
            np.save(file, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def save_object_data(file_path: str, obj: object) -> None:
    try:
        logging.info(f"Saving object to: {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as file:
            pickle.dump(obj, file)
        logging.info(f"Object saved to: {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e, sys)