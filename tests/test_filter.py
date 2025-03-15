import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from azure_region_validator.filter import filter_regions

def test_filter_regions():
    regions = ['eastus', 'westus']
    config = {'excluded_regions': ['westus']}
    filtered_regions = filter_regions(regions, config)
    assert filtered_regions == ['eastus']