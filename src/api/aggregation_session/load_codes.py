from src.utils.http import APIClient
import requests

def load_codes(client: APIClient, **kwargs) -> requests.Response:
    """
        Buffer Kity Load Codes

        

        Endpoint: /api/web/v1/aggregation_session/buffer/kity/load_codes
        Method: POST

        Parameters:
        - sscc_type (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/buffer/kity/load_codes"
    return client.request("POST", endpoint, **kwargs)
