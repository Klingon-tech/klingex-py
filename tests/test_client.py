"""
Tests for KlingEx Python SDK
"""

import pytest
from unittest.mock import Mock, patch

from klingex import (
    KlingEx,
    OrderSide,
    OrderType,
    KlingExError,
    AuthenticationError,
)


class TestKlingExClient:
    """Test the main KlingEx client"""

    def test_client_initialization(self):
        """Test client can be initialized"""
        client = KlingEx()
        assert client.markets is not None
        assert client.orders is not None
        assert client.wallet is not None
        assert client.invoices is not None
        client.close()

    def test_client_with_credentials(self):
        """Test client initialization with API credentials"""
        client = KlingEx(
            api_key="test_key",
            api_secret="test_secret",
        )
        assert client._http.api_key == "test_key"
        assert client._http.api_secret == "test_secret"
        client.close()

    def test_client_context_manager(self):
        """Test client works as context manager"""
        with KlingEx() as client:
            assert client is not None

    def test_custom_base_url(self):
        """Test client with custom base URL"""
        client = KlingEx(base_url="https://custom.api.com")
        assert client._http.base_url == "https://custom.api.com"
        client.close()


class TestOrderTypes:
    """Test order-related types"""

    def test_order_side_values(self):
        """Test OrderSide enum values"""
        assert OrderSide.BUY.value == "buy"
        assert OrderSide.SELL.value == "sell"

    def test_order_type_values(self):
        """Test OrderType enum values"""
        assert OrderType.LIMIT.value == "limit"
        assert OrderType.MARKET.value == "market"


class TestErrors:
    """Test error classes"""

    def test_klingex_error(self):
        """Test KlingExError"""
        error = KlingExError("Test error", status_code=400, code="TEST_ERROR")
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.code == "TEST_ERROR"

    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError("Invalid API key")
        assert error.message == "Invalid API key"
        assert isinstance(error, KlingExError)


class TestHttpClient:
    """Test HTTP client functionality"""

    @patch("httpx.Client.request")
    def test_get_request(self, mock_request):
        """Test GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response

        client = KlingEx()
        result = client._http.get("/test")

        assert result == {"data": "test"}
        client.close()

    @patch("httpx.Client.request")
    def test_error_handling(self, mock_request):
        """Test error response handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_request.return_value = mock_response

        client = KlingEx()

        with pytest.raises(AuthenticationError) as exc_info:
            client._http.get("/test", authenticated=True)

        assert "Unauthorized" in str(exc_info.value)
        client.close()
