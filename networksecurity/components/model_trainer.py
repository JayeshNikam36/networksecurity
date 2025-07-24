import os
import sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_util.utils import save_object_data, load_object
from networksecurity.utils.main_util.utils import load_numpy_array
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from networksecurity.utils.main_util.utils import evaluate_models

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def train_model(self, x_train, y_train,x_test, y_test) -> NetworkModel:
        models = {
            'logistic_regression': LogisticRegression(solver='saga', max_iter=1000),
            'knn': KNeighborsClassifier(),
            'decision_tree': DecisionTreeClassifier(),
            'random_forest': RandomForestClassifier(),
            'adaboost': AdaBoostClassifier(),
            'gradient_boosting': GradientBoostingClassifier()
        }

        params = {
                "logistic_regression": [
                    {
                        'penalty': ['l1', 'l2'],
                        'C': [0.001, 0.01, 0.1, 1.0],
                        'solver': ['saga'],
                        'max_iter': [1000]
                    },
                    {
                        'penalty': ['elasticnet'],
                        'C': [0.001, 0.01, 0.1, 1.0],
                        'l1_ratio': [0.0, 0.5, 1.0],
                        'solver': ['saga'],
                        'max_iter': [1000]
                    }
                ],
                "knn": {
                    'n_neighbors': [3, 5, 7, 9]
                },
                "decision_tree": {
                    'criterion': ['gini', 'entropy', 'log_loss']
                },
                "random_forest": {
                    'n_estimators': [64, 128],
                    'criterion': ['gini', 'entropy']
                },
                "adaboost": {
                    'n_estimators': [50, 100],
                    'learning_rate': [0.1, 0.5, 1.0]
                },
                "gradient_boosting": {
                    'n_estimators': [50, 100],
                    'learning_rate': [0.1, 0.2],
                    'criterion': ['friedman_mse', 'squared_error']
                }
            }


        model_report:dict = evaluate_models(
                            models=models,
                            params=params,
                            X_train=x_train,
                            y_train=y_train,
                            X_test=x_test,
                            y_test=y_test
                        )
        best_model_score = max(sorted(model_report.values()))

        best_model_name =list(model_report.keys())[
            list(model_report.values()).index(best_model_score)]
        best_model = models[best_model_name]
        y_train_pred = best_model.predict(x_train)
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        ##track the mlflow
        y_test_pred = best_model.predict(x_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path = os.path.dirname(self.model_trainer_config.model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        Network_model = NetworkModel(model=best_model, preprocessor=preprocessor)
        save_object_data(self.model_trainer_config.model_file_path, obj = Network_model)

        model_trainer_artifact = ModelTrainerArtifact(
                                            trained_model_file_path=self.model_trainer_config.model_file_path,
                                            train_metric_artifact=classification_train_metric,
                                            test_metric_artifact=classification_test_metric
                                        )
        logging.info("Model training completed successfully.")
        return model_trainer_artifact


    
    def initiate_model_training(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            train_arr = load_numpy_array(train_file_path)
            test_arr = load_numpy_array(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1], 
                train_arr[:, -1],
                test_arr[:, :-1], 
                test_arr[:, -1]

            )

            model = self.train_model(x_train, y_train, x_test, y_test)
            return model
        except Exception as e:
            raise NetworkSecurityException(e, sys)

