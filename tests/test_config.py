import pytest
from azure_region_validator.config import load_config

def test_load_config():
    config = load_config('path/to/config.json')
    assert 'excluded_regions' in config