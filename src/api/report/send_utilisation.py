from src.utils.http import APIClient
import requests
from src.models import UtilisationInput

def send_utilisation(client: APIClient, body: UtilisationInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Utilisation

        Отправить отчет о нанесение.

        Endpoint: /api/web/v1/report/send_utilisation
        Method: POST

        Parameters:
        - work_shift_id (string): 
        - id_agg_session (string): 
        - production_date (string): 
        - exp_date (string): 
        - inn (string): 
        - kpp (string): 
        - fias_id (string): 
        - vetis_guid (string): Идентификатор производственной площадки ВЕТИС
        - series_number (string): Номер серии
        - batch_number (string): Номер партии
        - alcohol_volume (string): 
        - document_number (string): 
        - document_date (string): 
        """
    endpoint = "/api/web/v1/report/send_utilisation"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)