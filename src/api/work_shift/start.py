from src.utils.http import APIClient
import requests
from src.models import WorkShiftStart

def start(client: APIClient, body: WorkShiftStart | dict | None = None, **kwargs) -> requests.Response:
    """
        Start

        Запустить производственную партию.

        Endpoint: /api/web/v1/work_shift/start
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - name (string): 
        - start_date (string): 
        - is_allow_other_gtins (boolean): 
        - product_group (ProductGroup): 
        - with_variable_weight (boolean): 
        - production_date (string): 
        - camera_is_active (boolean): 
        """
    endpoint = "/api/web/v1/work_shift/start"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)