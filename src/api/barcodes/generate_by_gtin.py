from src.utils.http import APIClient
import requests
from src.models import BarcodesGtinInput

def generate_by_gtin(client: APIClient, body: BarcodesGtinInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Pdf With Barcodes

        Получить pdf файл с штрих-кодами по ГТИНу и типу.

        Endpoint: /api/web/v1/barcodes/generate_by_gtin
        Method: POST

        Parameters:
        - gtin (string) (required): 
        - type (api__web__v1__aggregation_session__models__SSCC_TYPE) (required): 
        - count_codes (integer) (required): 
        - count_copies (integer): 
        - layout_id (string) (required): 
        - production_date (string): 
        """
    endpoint = "/api/web/v1/barcodes/generate_by_gtin"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)