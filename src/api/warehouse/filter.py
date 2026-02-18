from src.utils.http import APIClient
import requests
# FIXED: removed broken import of api__web__v1__warehouse__models__FilterInput

def filter(client: APIClient, body: dict | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Фильтрация по полученным ролику.

        Endpoint: /api/web/v1/warehouse/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - load_date_start (string): 
        - load_date_end (string): 
        - unit_serial_number (string): 
        - is_archived (boolean): 
        - report_sender_name (string): 
        - code (string): 
        - gtin (string): GTIN товара
        - good_name (string): 
        - empty_available_codes (boolean): 
        - product_group (string): 
        - exp_date_start (string): 
        - exp_date_end (string): 
        - total_codes_min (integer): 
        - total_codes_max (integer): 
        """
    endpoint = "/api/web/v1/warehouse/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)
