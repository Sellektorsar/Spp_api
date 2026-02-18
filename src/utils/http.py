import requests
from typing import Optional, Dict


class APIClient:
    def __init__(
        self,
        base_url: str,
        token: str = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def set_token(self, token: str) -> None:
        """Установить/обновить Bearer-токен авторизации."""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
                **kwargs,
            )
            return response
        except requests.RequestException as e:
            raise e
