from src.utils.http import APIClient
import requests
from src.models import CreateInput

def create(client: APIClient, body: CreateInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Create

        Создать рабочую линию.

        Endpoint: /api/web/v1/line/create
        Method: POST

        Parameters:
        - name (string) (required): 
        - line_type (LINE_TYPE) (required): 
        - product_group (ProductGroup) (required): 
        - production_type (ProductionType) (required): 
        - line_number (integer): 
        - camera_host (string): 
        - pin_code (string): 
        - is_auto_send_report (boolean): 
        - count_in_report (integer): 
        - report_to_send (array): 
        """
    endpoint = "/api/web/v1/line/create"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)