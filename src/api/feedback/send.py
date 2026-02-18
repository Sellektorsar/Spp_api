from src.utils.http import APIClient
import requests
from src.models import SendFeedbackIn

def send(client: APIClient, body: SendFeedbackIn | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Feedback

        Отправить обратную связь.

        Endpoint: /api/web/v1/feedback/send
        Method: POST

        Parameters:
        - company (string) (required): 
        - fio (string): 
        - email (string): 
        - summary (string) (required): 
        - description (string) (required): 
        """
    endpoint = "/api/web/v1/feedback/send"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)