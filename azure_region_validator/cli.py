import argparse
import logging
import json
from azure_region_validator.azure_api import get_regions
from azure_region_validator.config import load_config
from azure_region_validator.filter import filter_regions

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Azure Region Validator')
    parser.add_argument('--subscription-id', required=True, help='Azure Subscription ID')
    parser.add_argument('--config-file', required=True, help='Path to configuration file')
    args = parser.parse_args()

    try:
        config = load_config(args.config_file)
        regions = get_regions(args.subscription_id)
        filtered_regions = filter_regions(regions, config)
        logger.info(f'Filtered Regions: {filtered_regions}')

        output = {'filtered_regions': filtered_regions}
        print(json.dumps(output, indent=2))
    except Exception as e:
        logger.error(f'Error: {e}')
        raise

if __name__ == '__main__':
    main()