from src.utils.http import APIClient
import requests
from src.models import CirculationInput

def send_circulation(client: APIClient, body: CirculationInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send Circulation

        Отправить отчет о вводе в оборот.

        Endpoint: /api/web/v1/report/send_circulation
        Method: POST

        Parameters:
        - work_shift_id (string): 
        - id_agg_session (string): 
        - shipment_id (string): 
        - inn (string) (required): 
        - production_date (string): 
        - certificate_type (CERTIFICATE_TYPE): 
        - certificate_number (string): 
        - certificate_date (string): 
        - tnv (string): 
        - well_number (string): 
        - vsd (string): 
        - licences (api__web__v1__report__models__Licence): 
        - owner_inn (string): 
        - import_date (string): 
        - primary_document_date (string): 
        - primary_document_number (string): 
        - declaration_number (string): 
        - declaration_date (string): 
        - atk (string): 
        - color (string): 
        - product_size (string): 
        - trade_participant_kpp (string): 
        - cost (integer): 
        - vat_value (integer): 
        - excise (integer): 
        - tax_number (string): ИНН (или аналог) экспортёра
        - exporter_name (string): Наименование экспортёра
        - exporter_country (ExporterCountries): 
        """
    endpoint = "/api/web/v1/report/send_circulation"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)