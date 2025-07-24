import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os
import sys
import numpy as np
import dill
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

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
    
def load_object(file_path: str) -> object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        with open(file_path, 'rb') as file:
            print(file)
            return pickle.load(file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def load_numpy_array(file_path: str) -> np.array:
    try:
        with open(file_path, 'rb') as file:
            return np.load(file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)  
    
def evaluate_models(X_train, y_train, X_test, y_test, models, params):
    try:
        reports = {}

        for i, key in enumerate(models.keys()):
            model = list(models.values())[i]
            logging.info(f"Evaluating model: {key}")
            if key not in params:
                raise NetworkSecurityException(f"Parameters for model '{key}' not found.", sys)
            param = params[key]
            
            gs = GridSearchCV(model, param, cv=5)
            gs.fit(X_train, y_train)
            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            train_model_scorer = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)
            reports[list(models.keys())[i]] = test_model_score
        return reports
    except Exception as e:
        raise NetworkSecurityException(e, sys)