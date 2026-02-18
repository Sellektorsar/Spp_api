from src.utils.http import APIClient
import requests
from src.models import EditGtin

def edit(client: APIClient, body: EditGtin | dict | None = None, **kwargs) -> requests.Response:
    """
        Edit

        Редактировать записи в реестр.

        Endpoint: /api/web/v1/gtin/edit
        Method: POST

        Parameters:
        - gtin (string) (required): 
        - good_name (string): 
        - brand_name (string): 
        - is_required_vsd (boolean): 
        - tnved_code (string): 
        - certificate_type (integer): 
        - certificate_number (string): 
        - certificate_date (string): 
        - is_required_variable_weight (boolean): 
        - variable_weight (number): 
        - exp_date_delta (integer): 
        - package_gtin (array): 
        - product_group (ProductGroup): 
        - well_number (string): 
        - licences (LicencesGtin): 
        - kpp (string): 
        - fias_id (string): 
        - alcohol_volume (string): 
        - tax_number (string): ИНН (или аналог) экспортёра
        - exporter_name (string): Наименование экспортёра
        - exporter_country (ExporterCountries): 
        - owner_inn (string): 
        - producer_inn (string): 
        - is_required_certificate (boolean): 
        """
    endpoint = "/api/web/v1/gtin/edit"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)