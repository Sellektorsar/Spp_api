from src.utils.http import APIClient
import requests
from src.models import BufferKinStatisticInput

def statistics(client: APIClient, body: BufferKinStatisticInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Buffer Kigu Load From Order

        

        Endpoint: /api/web/v1/aggregation_session/buffer/kin/statistics
        Method: POST

        Parameters:
        - gtin_kin (string): ГТИН КИН
        - gtin_code (string): ГТИН КМ
        """
    endpoint = "/api/web/v1/aggregation_session/buffer/kin/statistics"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)