"""
KlingEx HTTP Client
"""

from typing import Any, Dict, Optional

import httpx


class KlingExError(Exception):
    """Base exception for KlingEx SDK"""

    def __init__(self, message: str, status_code: Optional[int] = None, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class AuthenticationError(KlingExError):
    """Authentication failed"""
    pass


class RateLimitError(KlingExError):
    """Rate limit exceeded"""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=429, code="RATE_LIMIT")
        self.retry_after = retry_after


class ValidationError(KlingExError):
    """Request validation failed"""
    pass


class HttpClient:
    """HTTP client for KlingEx API"""

    DEFAULT_BASE_URL = "https://api.klingex.io"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        """Close the HTTP client"""
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authentication headers"""
        if not self.api_key:
            raise AuthenticationError("API key is required for authenticated requests")

        return {
            "X-API-Key": self.api_key,
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        """Process API response and handle errors"""
        # Rate limit handling
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )

        # Try to parse JSON
        try:
            data = response.json()
        except Exception:
            if response.status_code >= 400:
                raise KlingExError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )
            return response.text

        # Handle error responses
        if response.status_code >= 400:
            error_message = data.get("error") or data.get("message") or str(data)
            error_code = data.get("code")

            if response.status_code == 401:
                raise AuthenticationError(error_message, status_code=401, code=error_code)
            elif response.status_code == 400:
                raise ValidationError(error_message, status_code=400, code=error_code)
            else:
                raise KlingExError(error_message, status_code=response.status_code, code=error_code)

        return data

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make an HTTP request"""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        # Add authentication headers
        if authenticated:
            auth_headers = self._get_auth_headers()
            headers.update(auth_headers)

        response = self._client.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
        )

        return self._handle_response(response)

    def request_bytes(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> bytes:
        """Make an HTTP request and return the raw response body.

        Used for endpoints that don't return JSON (e.g. invoice PDF
        downloads).
        """
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = {}
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if authenticated:
            headers.update(self._get_auth_headers())
        response = self._client.request(
            method=method, url=url, params=params, headers=headers,
        )
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        if response.status_code >= 400:
            # Try to surface the JSON error message if the server returned one.
            try:
                data = response.json()
                msg = data.get("error") or data.get("message") or str(data)
            except Exception:
                msg = f"HTTP {response.status_code}: {response.text[:200]}"
            if response.status_code == 401:
                raise AuthenticationError(msg, status_code=401)
            if response.status_code == 400:
                raise ValidationError(msg, status_code=400)
            raise KlingExError(msg, status_code=response.status_code)
        return response.content

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make a GET request"""
        return self.request("GET", path, params=params, authenticated=authenticated)

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make a POST request"""
        return self.request("POST", path, params=params, data=data, authenticated=authenticated)

    def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make a PUT request"""
        return self.request("PUT", path, data=data, authenticated=authenticated)

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make a DELETE request"""
        return self.request("DELETE", path, params=params, authenticated=authenticated)


class AsyncHttpClient:
    """Async HTTP client for KlingEx API"""

    DEFAULT_BASE_URL = "https://api.klingex.io"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        """Close the HTTP client"""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncHttpClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authentication headers"""
        if not self.api_key:
            raise AuthenticationError("API key is required for authenticated requests")

        return {
            "X-API-Key": self.api_key,
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        """Process API response and handle errors"""
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )

        try:
            data = response.json()
        except Exception:
            if response.status_code >= 400:
                raise KlingExError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )
            return response.text

        if response.status_code >= 400:
            error_message = data.get("error") or data.get("message") or str(data)
            error_code = data.get("code")

            if response.status_code == 401:
                raise AuthenticationError(error_message, status_code=401, code=error_code)
            elif response.status_code == 400:
                raise ValidationError(error_message, status_code=400, code=error_code)
            else:
                raise KlingExError(error_message, status_code=response.status_code, code=error_code)

        return data

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make an async HTTP request"""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        if authenticated:
            auth_headers = self._get_auth_headers()
            headers.update(auth_headers)

        response = await self._client.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
        )

        return self._handle_response(response)

    async def request_bytes(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> bytes:
        """Async variant of :meth:`HttpClient.request_bytes`."""
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = {}
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if authenticated:
            headers.update(self._get_auth_headers())
        response = await self._client.request(
            method=method, url=url, params=params, headers=headers,
        )
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        if response.status_code >= 400:
            try:
                data = response.json()
                msg = data.get("error") or data.get("message") or str(data)
            except Exception:
                msg = f"HTTP {response.status_code}: {response.text[:200]}"
            if response.status_code == 401:
                raise AuthenticationError(msg, status_code=401)
            if response.status_code == 400:
                raise ValidationError(msg, status_code=400)
            raise KlingExError(msg, status_code=response.status_code)
        return response.content

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make an async GET request"""
        return await self.request("GET", path, params=params, authenticated=authenticated)

    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make an async POST request"""
        return await self.request("POST", path, params=params, data=data, authenticated=authenticated)

    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make an async PUT request"""
        return await self.request("PUT", path, data=data, authenticated=authenticated)

    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """Make an async DELETE request"""
        return await self.request("DELETE", path, params=params, authenticated=authenticated)
