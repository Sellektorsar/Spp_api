from src.utils.http import APIClient
import requests
from src.models import WorkShiftFlagGtinInput

def change_flag_other_gtin(client: APIClient, body: WorkShiftFlagGtinInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Change Flag Gtin

        Изменить параметр добавления в партию разных gtin.

        Endpoint: /api/web/v1/work_shift/change_flag_other_gtin
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        - is_allow_other_gtins (boolean) (required): 
        """
    endpoint = "/api/web/v1/work_shift/change_flag_other_gtin"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)