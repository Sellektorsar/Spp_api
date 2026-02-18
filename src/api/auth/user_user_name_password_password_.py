from src.utils.http import APIClient
import requests

def user_user_name_password_password_(client: APIClient, **kwargs) -> requests.Response:
    """
    4. 3.3. Метод получения bearer токена для авторизации через адресную строку в браузере (auth/user={user_name}&password={password})
    
    Endpoint: api/web/v1/auth/user={user_name}&password={password}
    Method: GET
    """
    endpoint = "api/web/v1/auth/user={user_name}&password={password}"
    return client.request("GET", endpoint, **kwargs)
