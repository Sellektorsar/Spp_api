from src.utils.http import APIClient
import requests
from src.models import AggSessionInput

def get_detail_info(client: APIClient, body: AggSessionInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Get Detail Info

        Получить детальной информацию по id сессии

        Endpoint: /api/web/v1/aggregation_session/pallets/get_detail_info
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/get_detail_info"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)