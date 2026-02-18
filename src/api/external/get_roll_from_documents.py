from src.utils.http import APIClient
import requests
# FIXED: removed broken import of api__web__v1__external__models__GetRollFromDocumentInput

def get_roll_from_documents(client: APIClient, body: dict | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Roll From Documents

        Получить список документов.

        Endpoint: /api/web/v1/external/get_roll_from_documents
        Method: POST

        Parameters:
        - page (integer): Номер отображаемой страницы
        - size (integer): Количество документов на странице
        - sender_ids (array): Идентификатор сервис-провайдера
        - receiver_ids (array): Идентификатор УОТа
        - load_date_start (string): Дата начала периода
        - load_date_end (string): Дата окончания периода
        - product_group (any): Товарная группа
        - unit_serial_number (string): Код типографского агрегата (ролика)
        - gtin (string): GTIN товара
        - order_id (array): Идентификатор заказа
        """
    endpoint = "/api/web/v1/external/get_roll_from_documents"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)
