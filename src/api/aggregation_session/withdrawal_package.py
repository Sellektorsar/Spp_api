from src.utils.http import APIClient
import requests
from src.models import WithdrawalPalletInput

def withdrawal_package(client: APIClient, body: WithdrawalPalletInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Withdrawal Package

        Изъять упаковку из палеты.

        Endpoint: /api/web/v1/aggregation_session/withdrawal_package
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        - package_code (any) (required): 
        - pallet_code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/withdrawal_package"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)