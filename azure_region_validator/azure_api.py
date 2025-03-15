from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

def get_regions(subscription_id):
    credential = DefaultAzureCredential()
    client = ResourceManagementClient(credential, subscription_id)
    regions = client.providers.list()
    return [region for region in regions]