"""
Author: Yolanda Dantas
Date: July 2022

"""
import pytest
import pandas as pd
import wandb

run = wandb.init(project="week_08_data_checks", job_type="data_checks")

def pytest_addoption(parser):
    """Create parse arguments to pytest"""
    parser.addoption("--reference_artifact", action="store")
    parser.addoption("--sample_artifact", action="store")
    parser.addoption("--ks_alpha", action="store")

@pytest.fixture(scope="session")
def data(request):

    reference_artifact = request.config.option.reference_artifact
    if reference_artifact is None:
        pytest.fail("--clean_data_artifact missing on command line")

    sample_artifact = request.config.option.sample_artifact
    if sample_artifact is None:
        pytest.fail("--sample_artifact missing on command line")

    local_path = run.use_artifact(reference_artifact).file()
    sample1 = pd.read_csv(local_path)

    local_path = run.use_artifact(sample_artifact).file()
    sample2 = pd.read_csv(local_path)

    return sample1, sample2

@pytest.fixture(scope="session")
def ks_alpha(request):

    ks_alpha_value = request.config.option.ks_alpha
    if ks_alpha_value is None:
        pytest.fail("--ks_alpha missing on commando line")

    return float(ks_alpha_value)
        