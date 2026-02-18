from src.utils.http import APIClient
import requests

def lose_pallet(client: APIClient, **kwargs) -> requests.Response:
    """
    68. [DEPRECATED] 68. 9.12. Метод закрытия палеты в агрегационной сессии (aggregation_session/сlose_pallet)
    
    Endpoint: api/web/v1/aggregation_session/сlose_pallet
    Method: POST
    """
    endpoint = "api/web/v1/aggregation_session/сlose_pallet"
    return client.request("POST", endpoint, **kwargs)
