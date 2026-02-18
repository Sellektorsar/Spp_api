from src.utils.http import APIClient
import requests
from src.models import BarcodesGenerateToFileInput

def generate_to_file(client: APIClient, body: BarcodesGenerateToFileInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Generate To File

        

        Endpoint: /api/web/v1/barcodes/generate_to_file
        Method: POST

        Parameters:
        - gtin (string) (required): 
        - type (api__web__v1__aggregation_session__models__SSCC_TYPE) (required): 
        - count_codes (integer): 
        """
    endpoint = "/api/web/v1/barcodes/generate_to_file"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)