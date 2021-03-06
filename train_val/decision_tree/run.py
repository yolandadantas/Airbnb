"""
Author: Yolanda Dantas
Date: July 2022
Implement a pipeline component to train a decision tree model.
"""

import argparse
import logging
import os

import yaml
import tempfile
import mlflow
from mlflow.models import infer_signature

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import wandb
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import plot_tree

# configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt='%d-%m-%Y %H:%M:%S')

# reference for a logging obj
logger = logging.getLogger()


#Custom Transformer that extracts columns passed as argument to its constructor 
class FeatureSelector( BaseEstimator, TransformerMixin ):
    #Class Constructor 
    def __init__( self, feature_names ):
        self.feature_names = feature_names 
    
    #Return self nothing else to do here    
    def fit( self, X, y = None ):
        return self 
    
    #Method that describes what we need this transformer to do
    def transform( self, X, y = None ):
        return X[ self.feature_names ]
        
# Handling categorical features 
class CategoricalTransformer( BaseEstimator, TransformerMixin ):
    # Class constructor method that takes one boolean as its argument
    def __init__(self, new_features=True):
        self.new_features = new_features
        self.colnames = None

    #Return self nothing else to do here    
    def fit( self, X, y = None ):
        return self 

    def get_feature_names(self):
        return self.colnames.tolist()

    def transform(self, X , y = None):
        df = X.copy()
        self.colnames = df.columns    
        
        return df

# transform numerical features
class NumericalTransformer( BaseEstimator, TransformerMixin ):
    # Class constructor method that takes a model parameter as its argument
    # model 0: minmax
    # model 1: standard
    # model 2: without scaler
    def __init__(self, model = 0, colnames=None):
        self.model = model
        self.colnames = colnames

    #Return self nothing else to do here    
    def fit( self, X, y = None ):
        return self

    # return columns names after transformation
    def get_feature_names(self):
        return self.colnames 

    #Transformer method we wrote for this transformer 
    def transform(self, X , y = None ):
        df = pd.DataFrame(X,columns=self.colnames)

        # update columns name
        self.colnames = df.columns.tolist()

        # minmax
        if self.model == 0: 
            scaler = MinMaxScaler()
            # transform data
            df = scaler.fit_transform(df)
        elif self.model == 1:
            scaler = StandardScaler()
            # transform data
            df = scaler.fit_transform(df)
        else:
            df = df.values

        return df

def process_args(args):

    # project name comes from config.yaml >> project_name: 
    run = wandb.init(job_type="train")

    logger.info("Downloading and reading train artifact")
    local_path = run.use_artifact(args.train_data).file()
    df_train = pd.read_csv(local_path)

    # Spliting train.csv into train and validation dataset
    logger.info("Spliting data into train/val")
    # split-out train/validation and test dataset
    x_train, x_val, y_train, y_val = train_test_split(df_train.drop(labels="price",axis=1),
                                                      df_train["price"],
                                                      test_size=0.30,
                                                      random_state=41,
                                                      shuffle=True,
                                                      stratify=df_train["room_type"])
    
    logger.info("x train: {}".format(x_train.shape))
    logger.info("y train: {}".format(y_train.shape))
    logger.info("x val: {}".format(x_val.shape))
    logger.info("y val: {}".format(y_val.shape))

    logger.info("Removal Outliers")
    # temporary variable
    x = x_train.select_dtypes(["int64", "float"]).copy()

    # identify outlier in the dataset
    lof = LocalOutlierFactor()
    outlier = lof.fit_predict(x)
    mask = outlier != -1

    logger.info("x_train shape [original]: {}".format(x_train.shape))
    logger.info("x_train shape [outlier removal]: {}".format(x_train.loc[mask,:].shape))

    # dataset without outlier, note this step could be done during the preprocesing stage
    x_train = x_train.loc[mask,:].copy()
    y_train = y_train[mask].copy()
  
    # Pipeline generation
    logger.info("Pipeline generation")
    
    # Get the configuration for the pipeline
    with open(args.model_config) as fp:
        model_config = yaml.safe_load(fp)
        
    # Add it to the W&B configuration so the values for the hyperparams
    # are tracked
    wandb.config.update(model_config)
    
    # Categrical features to pass down the categorical pipeline 
    categorical_features = x_train.select_dtypes("object").columns.to_list()

    # Numerical features to pass down the numerical pipeline 
    numerical_features = x_train.select_dtypes(["int64", "float"]).columns.to_list()

    # Defining the steps in the categorical pipeline 
    categorical_pipeline = Pipeline(steps = [('cat_selector',FeatureSelector(categorical_features)),
                                             ('cat_transformer', CategoricalTransformer()),
                                             #('cat_encoder','passthrough'
                                             ('cat_encoder',OneHotEncoder(sparse=False,drop="first"))
                                            ]
                                   )
    # Defining the steps in the numerical pipeline     
    numerical_pipeline = Pipeline(steps = [('num_selector', FeatureSelector(numerical_features)),
                                           ('num_transformer', NumericalTransformer((model_config["numerical_pipe"]["model"])))
                                          ]
                                 )

    # Combining numerical and categorical piepline into one full big pipeline horizontally 
    # using FeatureUnion
    full_pipeline_preprocessing = FeatureUnion(transformer_list = [('cat_pipeline', categorical_pipeline),
                                                                   ('num_pipeline', numerical_pipeline)
                                                                  ]
                                              )
   
    
    # The full pipeline 
    pipe = Pipeline(steps = [('full_pipeline', full_pipeline_preprocessing),
                             ("regressor",DecisionTreeRegressor())
                            ]
                   )

    # training 
    logger.info("Training")
    pipe.fit(x_train,y_train)

    # predict
    logger.info("Infering")
    predict = pipe.predict(x_val)
    
    # Evaluation Metrics
    logger.info("Evaluation metrics")
    # Metric: Mean Absolute Error
    mae = mean_absolute_error(y_val, predict)
    run.summary["MAE"] = mae
    
    # Metric: Root Mean Squared Srror 
    rmse = np.sqrt(mean_squared_error(y_val, predict))
    run.summary["RMSE"] = rmse

    # full pipeline
    features_full = pipe.named_steps['full_pipeline']

    # get columns names from categorial columns
    features_cat = features_full.get_params()["cat_pipeline"]
    features_cat = features_cat[2].get_feature_names_out().tolist()
    
    # get columns names from numerical columns
    features_num = features_full.get_params()["num_pipeline"][1].get_feature_names()

    fig_tree, ax_tree = plt.subplots(1,1, figsize=(15, 10))
    plot_tree(pipe["regressor"], 
              filled=True, 
              rounded=True, 
              feature_names=features_cat+features_num, ax=ax_tree, fontsize=2)

    # Uploading figure
    logger.info("Uploading figure")
    run.log(
        {
            "tree": wandb.Image(fig_tree)
        }
    )
    
    # Export if required
    if args.export_artifact != "null":
        export_model(run, pipe, x_val, predict, args.export_artifact)

        
def export_model(run, pipe, x_val, val_pred, export_artifact):

    # Infer the signature of the model
    signature = infer_signature(x_val, val_pred)

    with tempfile.TemporaryDirectory() as temp_dir:

        export_path = os.path.join(temp_dir, "model_export")

        mlflow.sklearn.save_model(
            pipe, # our pipeline
            export_path, # Path to a directory for the produced package
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
            signature=signature, # input and output schema
            input_example=x_val.iloc[:2], # the first few examples
        )

        artifact = wandb.Artifact(
            export_artifact,
            type="model_export",
            description="Decision Tree pipeline export",
        )
        
        # NOTE that we use .add_dir and not .add_file
        # because the export directory contains several
        # files
        artifact.add_dir(export_path)

        run.log_artifact(artifact)

        # Make sure the artifact is uploaded before the temp dir
        # gets deleted
        artifact.wait()        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train a Decision Tree",
        fromfile_prefix_chars="@",
    )
    
    parser.add_argument(
        "--train_data",
        type=str,
        help="Fully-qualified name for the training data artifact",
        required=True,
    )

    parser.add_argument(
        "--model_config",
        type=str,
        help="Path to a YAML file containing the configuration for the Decision Tree",
        required=True,
    )

    parser.add_argument(
        "--export_artifact",
        type=str,
        help="Name of the artifact for the exported model. Use 'null' for no export.",
        required=False,
        default="null"
    )

    ARGS = parser.parse_args()

    process_args(ARGS)
