import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from azure_region_validator.config import load_config
from io import StringIO

def test_load_config(monkeypatch):
    # Mock the open function to return a sample config
    sample_config = {
        "subscription_id": "test-sub",
        "resource_group": "test-rg",
        "location": "eastus"
    }
    monkeypatch.setattr('builtins.open', lambda f, _: StringIO(json.dumps(sample_config)))
    config = load_config('path/to/config.json')
    assert config['subscription_id'] == 'test-sub'
    assert config['resource_group'] == 'test-rg'
    assert config['location'] == 'eastus'