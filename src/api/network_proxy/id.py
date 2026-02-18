from src.utils.http import APIClient
import requests

def id(client: APIClient, **kwargs) -> requests.Response:
    """
    203. [DEPRECATED] 203. 23.12. Метод скачивания отчета (документа) (orders/download/reportCsv/{id})
    
    Endpoint: api/network_proxy/api/network/v1/orders/download/reportCsv/{id}
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/download/reportCsv/{id}"
    return client.request("GET", endpoint, **kwargs)
