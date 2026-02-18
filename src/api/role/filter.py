from src.utils.http import APIClient
import requests
# FIXED: removed broken import of api__web__v1__role__models__FilterInput

def filter(client: APIClient, body: dict | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        

        Endpoint: /api/web/v1/role/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - role_name (string): 
        """
    endpoint = "/api/web/v1/role/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)
