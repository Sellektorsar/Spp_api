from src.utils.http import APIClient
import requests
# FIXED: removed broken import of api__web__v1__line__models__DeleteInput

def delete(client: APIClient, body: dict | dict | None = None, **kwargs) -> requests.Response:
    """
        Delete

        Удалить рабочую линию.

        Endpoint: /api/web/v1/line/delete
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        """
    endpoint = "/api/web/v1/line/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)
