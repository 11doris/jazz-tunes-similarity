import json
import os
import tempfile
import time
import datetime
import pytest


FIXTURE_DIR = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture(scope='module')
def tests_config():
    config_file_path = get_test_root_file("tests/config.json")
    env_var = os.environ.get('TESTS_CONFIG_FILE')
    if env_var is not None:
        config_file_path = get_test_root_file("tests/" + env_var)

    with open(config_file_path) as config_file:
        data = json.load(config_file)
    return data

# @pytest.fixture(scope='module')
# def etl_config():
#     config_file_path = get_test_root_file("etl-config.json")
#     with open(config_file_path) as config_file:
#         return EtlConfig(config_file.read())


def get_test_root_path(path):
    f = os.path.normpath(os.path.join(FIXTURE_DIR, "../"))
    return os.path.join(f, path)


def get_test_root_file(file):
    f = os.path.normpath(os.path.join(FIXTURE_DIR, "../", file))
    if not os.path.isfile(f):
        raise Exception("File not found: " + f)
    return f
