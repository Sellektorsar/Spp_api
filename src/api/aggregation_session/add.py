from src.utils.http import APIClient
import requests
from src.models import PresetAddInput

def add(client: APIClient, body: PresetAddInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Agg Preset

        Добавление пресета.

        Endpoint: /api/web/v1/aggregation_session/preset/add
        Method: POST

        Parameters:
        - name (string) (required): 
        - line_number (integer) (required): 
        - read_type (api__web__v1__aggregation_session__models__READ_TYPE) (required): 
        - package_settings (UnitSettings) (required): 
        - pallet_settings (UnitSettings): 
        """
    endpoint = "/api/web/v1/aggregation_session/preset/add"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)