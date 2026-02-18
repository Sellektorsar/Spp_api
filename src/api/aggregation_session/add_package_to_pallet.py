from src.utils.http import APIClient
import requests
from src.models import AddPackageToPallet

def add_package_to_pallet(client: APIClient, body: AddPackageToPallet | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Package To Pallet

        Добавить упаковку в палету.

        Endpoint: /api/web/v1/aggregation_session/add_package_to_pallet
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        - package_code (any) (required): 
        - pallet_code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/add_package_to_pallet"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)