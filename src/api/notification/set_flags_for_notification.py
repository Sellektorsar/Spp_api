from src.utils.http import APIClient
import requests
from src.models import FlagsInput

def set_flags_for_notification(client: APIClient, body: FlagsInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Set Flags For Notification

        Выставить параметры отправки уведомлений.

        Endpoint: /api/web/v1/notification/set_flags_for_notification
        Method: POST

        Parameters:
        - report_error_scheduler (boolean): 
        - work_shift_scheduler (boolean): 
        - agg_session_scheduler (boolean): 
        - order_scheduler (boolean): 
        """
    endpoint = "/api/web/v1/notification/set_flags_for_notification"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)