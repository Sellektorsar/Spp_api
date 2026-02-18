from src.utils.http import APIClient
import requests
from src.models import AggSessionAddCodeScanner

def add_code(client: APIClient, body: AggSessionAddCodeScanner | dict | None = None, **kwargs) -> requests.Response:
    """
        Vision Add Code

        Добавление кода с внешнего устройства при работе через сканер.

        Endpoint: /api/web/v1/aggregation_session/vision/scanner/add_code
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/vision/scanner/add_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)