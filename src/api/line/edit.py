from src.utils.http import APIClient
import requests

def edit(client: APIClient, body: dict | None = None, **kwargs) -> requests.Response:
    """
        Edit

        Изменить данные для рабочей линии.

        Endpoint: /api/web/v1/line/edit
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - name (string): 
        - product_group (ProductGroup): 
        - production_type (ProductionType): 
        - camera_host (string): 
        - pin_code (string): 
        - is_auto_send_report (boolean): 
        - count_in_report (integer): 
        - report_to_send (array): 
        """
    endpoint = "/api/web/v1/line/edit"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)