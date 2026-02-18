from src.utils.http import APIClient
import requests

def user_user_name_password_password(client: APIClient, **kwargs) -> requests.Response:
    """
        Authenticate With Address Bar

        Получить bearer токен для авторизации через адресную строку в браузере.

        Endpoint: /api/web/v1/auth/user={user_name}&password={password}
        Method: GET

        Parameters:
        - user_name (string) (required): 
        - password (string) (required): 
        """
    endpoint = "/api/web/v1/auth/user={user_name}&password={password}"
    return client.request("GET", endpoint, **kwargs)
