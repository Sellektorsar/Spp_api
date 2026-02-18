from src.utils.http import APIClient
import requests
from src.models import SendAggregationInput

def send_aggregation(client: APIClient, body: SendAggregationInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Aggregation

        Отправить отчет агрегации.

        Endpoint: /api/web/v1/report/send_aggregation
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        - inn (string): ИНН собственника товара
        """
    endpoint = "/api/web/v1/report/send_aggregation"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)