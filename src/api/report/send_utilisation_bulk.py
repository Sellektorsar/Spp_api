from src.utils.http import APIClient
import requests
from src.models import UtilisationBulkInput

def send_utilisation_bulk(client: APIClient, body: UtilisationBulkInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Utilisation

        

        Endpoint: /api/web/v1/report/send_utilisation_bulk
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        - reports (array) (required): 
        """
    endpoint = "/api/web/v1/report/send_utilisation_bulk"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)