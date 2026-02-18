from src.utils.http import APIClient
import requests
from src.models import ReportFilterInput

def filter(client: APIClient, body: ReportFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Фильтрация по сформированным отчетам.

        Endpoint: /api/web/v1/report/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - id (string): 
        - status (integer): 
        - type (integer): 
        - created_date_start (string): 
        - created_date_end (string): 
        - work_shift_id (string): 
        - line_number (integer): 
        - gtin (string): 
        - report_id (string): 
        - code (string): 
        - source_report_id (string): 
        - agg_session_number (integer): 
        - unit_serial_number (string): 
        """
    endpoint = "/api/web/v1/report/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)