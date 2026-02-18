from src.utils.http import APIClient
import requests
from src.models import BufferKiguLoadOrder

def load_from_order(client: APIClient, body: BufferKiguLoadOrder | dict | None = None, **kwargs) -> requests.Response:
    """
        Buffer Kin Load From Order

        

        Endpoint: /api/web/v1/aggregation_session/buffer/kin/load_from_order
        Method: POST

        Parameters:
        - order_id (string) (required): Идентификатор заказа
        - chunk_size (integer) (required): Количество загружаемых кодов
        """
    endpoint = "/api/web/v1/aggregation_session/buffer/kin/load_from_order"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)