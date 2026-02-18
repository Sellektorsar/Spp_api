from src.utils.http import APIClient
import requests

def get_roll(client: APIClient, params: dict = None) -> requests.Response:
    """
    Get information about a roll and its composition.
    
    Endpoint: /api/web/v1/warehouse/get_roll
    Method: POST
    
    :param client: APIClient instance
    :param params: JSON body parameters (e.g., {"code": "..."})
    :return: requests.Response object
    """
    endpoint = "api/web/v1/warehouse/get_roll"
    return client.request("POST", endpoint, json=params)
