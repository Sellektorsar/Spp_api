from src.utils.http import APIClient
import requests
# FIXED: removed broken import of api__web__v1__printer__models__DeleteInput

def delete(client: APIClient, body: dict | dict | None = None, **kwargs) -> requests.Response:
    """
        Delete

        Удалить принтер.

        Endpoint: /api/web/v1/printer/delete
        Method: POST

        Parameters:
        - printer_id (string) (required): 
        """
    endpoint = "/api/web/v1/printer/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)
