import pytest
from azure_region_validator.filter import filter_regions

def test_filter_regions():
    regions = ['eastus', 'westus']
    config = {'excluded_regions': ['westus']}
    filtered_regions = filter_regions(regions, config)
    assert filtered_regions == ['eastus']