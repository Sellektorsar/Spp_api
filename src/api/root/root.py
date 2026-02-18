from src.utils.http import APIClient
import requests

def root(client: APIClient, **kwargs) -> requests.Response:
    """
    157. [DEPRECATED] 157. 14.5. Метод выгрузки статистики по отчетам за определенный период в формате «.xlsx» (report/download_excel)
    
    Endpoint: api/web/v1/
    Method: POST
    """
    endpoint = "api/web/v1/"
    return client.request("POST", endpoint, **kwargs)
