"""API Caller module for making HTTP requests to Maps API"""

import requests

from domain.exceptions import SeatingPlanException


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
            response = requests.get(
                url,
                headers=headers or self.HEADERS,
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            raise SeatingPlanException(f"API call failed for {endpoint}: {e}", error_code="API_REQUEST_FAILED")
