from src.utils.http import APIClient
import requests
from src.models import SendReAggregationInput

def send_reaggregation(client: APIClient, body: SendReAggregationInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Reaggregation

        

        Endpoint: /api/web/v1/report/send_reaggregation
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/report/send_reaggregation"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)