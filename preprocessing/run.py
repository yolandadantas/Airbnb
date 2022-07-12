"""
Author: Yolanda Dantas
Date: July 2022
This project fetches the raw data, cleans the data, and creates a new artifact in wandb project.
"""
import argparse
import logging
import os
import pandas as pd
import wandb

# configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt='%d-%m-%Y %H:%M:%S')

# reference for a logging obj
LOGGER = logging.getLogger()


def preprocess_data(raw_data):
    """Return the processed DataFrame
    Args:
        raw_data(pd.DataFrame): DataFrame to clean data
    Returns:
        (pd.DataFrame): Processed dataFrame
    """
    LOGGER.info("Selecting columns")
    columns = ['accommodates', 'bedrooms',
               'beds', 'price', 'number_of_reviews', 
               'minimum_nights', 'maximum_nights']
    raw_data = raw_data[columns]

    LOGGER.info("Dropping duplicates")
    raw_data = raw_data.drop_duplicates(ignore_index=True)

    LOGGER.info("Treating missing values")
    columns_drop = ['accommodates', 'bedrooms',
                    'beds', 'price', 'number_of_reviews']

    clean_data = raw_data.dropna(subset=columns_drop).reset_index(drop=True)

    return clean_data


def treat_bathroom_text(value):
    """Treat bathroom_text column
    Args:
        value(Any): Value from bathroom_text column
    Returns:
        (float): the float treated value for bathroom_text item
    """
    if not isinstance(value, str):
        return value

    try:
        return float(value.split(' ')[0])
    except ValueError as excep:
        LOGGER.debug(excep)
        return 0.5

def process_args(args):
    """Process args passed by command line
    Args:
        args - command line arguments
        args.input_artifact: Fully qualified name for the raw data artifact
        args.artifact_name: Name for the W&B artifact that will be created
        args.artifact_type: Type of the artifact to create
        args.artifact_description: Description for the artifact
        args.project_name: Name of WandB project you want to access/create
    """
    run = wandb.init(project=args.project_name,
                     job_type="preproccess_data")

    LOGGER.info("Dowloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    # create a dataframe from the artifact path
    df = pd.read_csv(artifact_path)

    LOGGER.info("Preprocessing dataset")
    clean_data = preprocess_data(raw_data)

    # Generate a "clean data file"
    filename = "preprocessed_data.csv"
    df.to_csv(filename,index=False)

    # Create a new artifact and configure with the necessary arguments"
    LOGGER.info("Creating W&B artifact")
    artifact = wandb.Artifact(
        name=args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description
    )
    artifact.add_file(filename)

    LOGGER.info("Logging artifact to wandb project")
    run.log_artifact(artifact)

   # Remote temporary files
    os.remove(filename)

    run.finish()

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Preproccess a dataset",
        fromfile_prefix_chars="@"
    )

    PARSER.add_argument(
        "--input_artifact",
        type=str,
        help="Fully qualified name for the input artifact",
        required=True
    )

    PARSER.add_argument(
        "--artifact_name", type=str, help="Name for the artifact", required=True
    )

    PARSER.add_argument(
        "--artifact_type", type=str, help="Type for the artifact", required=True
    )

    PARSER.add_argument(
        "--project_name",
        type=str,
        help="Name of WandB project you want to access/create",
        required=True
    )

    PARSER.add_argument(
        "--artifact_description",
        type=str,
        help="Description for the artifact",
        required=True
    )
    
    # get arguments
    ARGS = PARSER.parse_args()

    #process the arguments
    process_args(ARGS)