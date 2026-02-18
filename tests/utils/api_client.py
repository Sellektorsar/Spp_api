import requests
import logging
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.session.headers.update({"Content-Type": "application/json"})
        self.logger = logging.getLogger(__name__)

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self.logger.info(f"Request: {method} {url} - Params: {kwargs.get('params')} - Body: {kwargs.get('json')}")
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.info(f"Response: {response.status_code} - Body: {response.text[:200]}...")
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)
