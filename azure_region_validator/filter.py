def filter_regions(regions, config):
    filtered_regions = []
    for region in regions:
        if region not in config['excluded_regions']:
            filtered_regions.append(region)
    return filtered_regions