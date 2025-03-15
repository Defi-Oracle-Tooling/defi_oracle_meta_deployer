import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from azure_region_validator.azure_api import get_regions

def test_get_regions():
    # Mock Azure SDK response
    pass