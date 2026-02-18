from src.utils.http import APIClient
import requests

def get_flags_and_recipients(client: APIClient, **kwargs) -> requests.Response:
    """
        Get Flags And Recipients

        Данные по получателям и флагам отправки уведомлений.

        Endpoint: /api/web/v1/notification/get_flags_and_recipients
        Method: GET

        Parameters:
        """
    endpoint = "/api/web/v1/notification/get_flags_and_recipients"
    return client.request("GET", endpoint, **kwargs)
