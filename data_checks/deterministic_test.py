"""
Author: Yolanda Dantas
Date: July 2022
"""
import pytest
import wandb
import pandas as pd

# This is global so all tests are collected under the same
# run
run = wandb.init(project="week_08_data_checks", job_type="data_checks")


@pytest.fixture(scope="session")
def data():

    local_path = run.use_artifact("week_08_preprocessing/preprocessed_data.csv:latest").file()
    df = pd.read_csv(local_path)

    return df


def test_column_presence_and_type(data):
    """Check if dataset has all needed columns with the correct type"""

    required_columns = {
        "accommodates": pd.api.types.is_int64_dtype,
        "bedrooms": pd.api.types.is_float_dtype,
        "beds": pd.api.types.is_float_dtype,
        "price": pd.api.types.is_float_dtype,
        "number_of_reviews": pd.api.types.is_int64_dtype,
        "minimum_nights": pd.api.types.is_int64_dtype,
        "maximum_nights": pd.api.types.is_int64_dtype,
        "room_type": pd.api.types.is_object_dtype
    }

    # Check column presence
    assert set(data.columns.values).issuperset(set(required_columns.keys()))

    for col_name, format_verification_funct in required_columns.items():

        assert format_verification_funct(data[col_name]), \
            f"Column {col_name} failed test {format_verification_funct}"

def test_class_names(data):
    """Check that only the known classes are present"""
    known_classes = {
        'room_type': [
            'Entire home/apt',
            'Private room',
            'Shared room',
            'Hotel room'],
        }
    assert data["room_type"].isin(known_classes["room_type"]).all()
    
def test_column_ranges(data):
    """Check if all columns have meaningful data ranges"""

    ranges = {
        "accommodates": (0, 16),
        "bedrooms": (1.0, 47.0),
        "beds": (1.0, 91.0),
        "price": (0.0, 999999.0),
        "number_of_reviews": (0, 504),
        "minimum_nights": (1, 1000),
        "maximum_nights": (1, 47036)
    }

    for col_name, (minimum, maximum) in ranges.items():

        assert data[col_name].dropna().between(minimum, maximum).all(), (
            f"Column {col_name} failed the test. Should be between {minimum} and {maximum}, "
            f"instead min={data[col_name].min()} and max={data[col_name].max()}"
        )
