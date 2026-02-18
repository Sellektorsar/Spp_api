from src.utils.http import APIClient
import requests
from src.models import ReportExcelInput

def download_excel(client: APIClient, body: ReportExcelInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Download Excel

        Скачать excel файл со всеми отчетами

        Endpoint: /api/web/v1/report/download_excel
        Method: POST

        Parameters:
        - date_start (string) (required): 
        - date_end (string) (required): 
        """
    endpoint = "/api/web/v1/report/download_excel"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)