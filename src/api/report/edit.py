from src.utils.http import APIClient
import requests
# FIXED: removed broken import of api__web__v1__report__models__EditInput

def edit(client: APIClient, body: dict | dict | None = None, **kwargs) -> requests.Response:
    """
        Edit Report

        Редактировать отчет.

        Endpoint: /api/web/v1/report/edit
        Method: POST

        Parameters:
        - report_id (string) (required): 
        - exp_date (string): 
        - inn (string): 
        - production_date (string): 
        - tnv (string): 
        - certificate_type (CERTIFICATE_TYPE): 
        - certificate_number (string): 
        - certificate_date (string): 
        - well_number (string): 
        - licences (api__web__v1__report__models__Licence): 
        - vsd (string): 
        - owner_inn (string): 
        - import_date (string): 
        - primary_document_date (string): 
        - primary_document_number (string): 
        - declaration_number (string): 
        - declaration_date (string): 
        - atk (string): 
        - color (string): 
        - product_size (string): 
        - kpp (string): 
        - fias_id (string): 
        - vetis_guid (string): Идентификатор производственной площадки ВЕТИС
        - series_number (string): Номер серии
        - trade_participant_kpp (string): 
        - cost (integer): 
        - vat_value (integer): 
        - excise (integer): 
        - batch_number (string): Номер партии
        - alcohol_volume (string): 
        - document_number (string): 
        - document_date (string): 
        - tax_number (string): ИНН (или аналог) экспортёра
        - exporter_name (string): Наименование экспортёра
        - exporter_country (ExporterCountries): 
        """
    endpoint = "/api/web/v1/report/edit"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)
