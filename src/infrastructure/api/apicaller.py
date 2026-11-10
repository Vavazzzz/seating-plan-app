"""API Caller module for making HTTP requests to Maps API"""

import ssl

import requests
import truststore
from requests.adapters import HTTPAdapter

from domain.exceptions import SeatingPlanException


class _OSTrustStoreAdapter(HTTPAdapter):
    """HTTPS adapter that verifies certificates against the OS trust store.

    certifi (requests' default bundle) lacks corporate TLS-inspection roots such
    as Zscaler's, which IT installs into the Windows store. Verification stays on.
    """

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        return super().init_poolmanager(*args, **kwargs)


class APICaller:
    """Handles API calls to Maps API endpoints"""
    
    # Browser-like headers to avoid being blocked
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    def __init__(self, base_url: str):
        """
        Initialize APICaller with base URL
        
        Args:
            base_url: The base URL for API calls
        """
        self.base_url = base_url
        self._session = requests.Session()
        self._session.mount("https://", _OSTrustStoreAdapter())

    TIMEOUT_SECONDS = 30

    def call_api(self, endpoint: str, headers: dict | None = None) -> dict | list:
        """
        Make an API call to the specified endpoint

        Args:
            endpoint: The endpoint path (will be appended to base_url)
            headers: Optional custom headers (defaults to HEADERS)

        Returns:
            Parsed JSON response

        Raises:
            SeatingPlanException: If the request fails or the body is not valid JSON
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self._session.get(
                url,
                headers=headers or self.HEADERS,
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            raise SeatingPlanException(f"API call failed for {endpoint}: {e}", error_code="API_REQUEST_FAILED")
