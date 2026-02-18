from src.utils.http import APIClient
import requests
from src.models import SendAtkInput

def send_atk(client: APIClient, body: SendAtkInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Atk

        Отправить отчет агрегации АТК.

        Endpoint: /api/web/v1/report/send_atk
        Method: POST

        Parameters:
        - work_shift_id (string): 
        - id_agg_session (string): 
        - shipment_id (string): 
        - inn (string) (required): 
        """
    endpoint = "/api/web/v1/report/send_atk"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)