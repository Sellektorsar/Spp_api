from src.utils.http import APIClient
import requests
from src.models import DownloadReport

def download(client: APIClient, body: DownloadReport | dict | None = None, **kwargs) -> requests.Response:
    """
        Download Reaggregation Csv

        Скачать файл отчета ре-агрегации

        Endpoint: /api/web/v1/report/reaggregation/download
        Method: POST

        Parameters:
        - report_id (string) (required): 
        - file_type (any): 
        """
    endpoint = "/api/web/v1/report/reaggregation/download"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)