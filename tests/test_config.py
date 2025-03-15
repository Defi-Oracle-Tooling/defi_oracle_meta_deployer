import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from azure_region_validator.config import load_config

def test_load_config():
    config = load_config('path/to/config.json')
    assert 'excluded_regions' in config