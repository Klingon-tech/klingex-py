"""
Invoices Endpoint - Payment invoice management
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Invoice, InvoiceListResponse, InvoiceFeeStats

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class InvoicesEndpoint:
    """Invoice management endpoints"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def create_invoice(
        self,
        currency: str,
        amount: str,
        accepted_coins: List[str],
        external_id: Optional[str] = None,
        expires_in_minutes: int = 30,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        buyer_email: Optional[str] = None,
        payment_tolerance: Optional[int] = None,
    ) -> Invoice:
        """Create a new payment invoice

        Args:
            currency: Denomination currency (e.g., "USDT", "BTC")
            amount: Human-readable amount (e.g., "100.00")
            accepted_coins: Asset symbols to accept (e.g., ["BTC", "ETH", "USDT"])
            external_id: Your reference ID (max 255 chars)
            expires_in_minutes: Expiration time (5-1440 min, default: 30)
            description: Description shown on payment page
            metadata: Custom data stored with invoice
            buyer_email: Buyer email for notifications
            payment_tolerance: Accept X% as full payment (90-100, default: 100)
        """
        data: Dict[str, Any] = {
            "denomination": {
                "currency": currency,
                "amount": amount,
            },
            "accepted_coins": accepted_coins,
            "expires_in_minutes": expires_in_minutes,
        }
        if external_id:
            data["external_id"] = external_id
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        if buyer_email:
            data["buyer_email"] = buyer_email
        if payment_tolerance:
            data["payment_tolerance"] = payment_tolerance

        response = self._client.post("/api/invoices", data=data, authenticated=True)
        return Invoice.model_validate(response.get("data", response))

    def list_invoices(
        self,
        status: Optional[str] = None,
        external_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> InvoiceListResponse:
        """List invoices with optional filters

        Args:
            status: Filter by status (pending, confirming, paid, overpaid, underpaid, expired, cancelled)
            external_id: Filter by your external reference ID
            page: Page number (default: 1)
            page_size: Items per page (1-100, default: 20)
        """
        params: Dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if status:
            params["status"] = status
        if external_id:
            params["external_id"] = external_id

        response = self._client.get("/api/invoices", params=params, authenticated=True)
        return InvoiceListResponse.model_validate(response.get("data", response))

    def get_invoice(self, invoice_id: str) -> Invoice:
        """Get invoice details

        Args:
            invoice_id: Invoice UUID
        """
        response = self._client.get(f"/api/invoices/{invoice_id}", authenticated=True)
        return Invoice.model_validate(response.get("data", response))

    def cancel_invoice(self, invoice_id: str) -> Dict[str, str]:
        """Cancel a pending invoice

        Args:
            invoice_id: Invoice UUID to cancel
        """
        return self._client.post(f"/api/invoices/{invoice_id}/cancel", authenticated=True)

    def get_fee_stats(self) -> InvoiceFeeStats:
        """Get invoice fee statistics"""
        response = self._client.get("/api/invoices/fees", authenticated=True)
        return InvoiceFeeStats.model_validate(response.get("data", response))


class AsyncInvoicesEndpoint:
    """Async invoice management endpoints"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def create_invoice(
        self,
        currency: str,
        amount: str,
        accepted_coins: List[str],
        external_id: Optional[str] = None,
        expires_in_minutes: int = 30,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        buyer_email: Optional[str] = None,
        payment_tolerance: Optional[int] = None,
    ) -> Invoice:
        """Create a new payment invoice"""
        data: Dict[str, Any] = {
            "denomination": {
                "currency": currency,
                "amount": amount,
            },
            "accepted_coins": accepted_coins,
            "expires_in_minutes": expires_in_minutes,
        }
        if external_id:
            data["external_id"] = external_id
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        if buyer_email:
            data["buyer_email"] = buyer_email
        if payment_tolerance:
            data["payment_tolerance"] = payment_tolerance

        response = await self._client.post("/api/invoices", data=data, authenticated=True)
        return Invoice.model_validate(response.get("data", response))

    async def list_invoices(
        self,
        status: Optional[str] = None,
        external_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> InvoiceListResponse:
        """List invoices with optional filters"""
        params: Dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if status:
            params["status"] = status
        if external_id:
            params["external_id"] = external_id

        response = await self._client.get("/api/invoices", params=params, authenticated=True)
        return InvoiceListResponse.model_validate(response.get("data", response))

    async def get_invoice(self, invoice_id: str) -> Invoice:
        """Get invoice details"""
        response = await self._client.get(f"/api/invoices/{invoice_id}", authenticated=True)
        return Invoice.model_validate(response.get("data", response))

    async def cancel_invoice(self, invoice_id: str) -> Dict[str, str]:
        """Cancel a pending invoice"""
        return await self._client.post(f"/api/invoices/{invoice_id}/cancel", authenticated=True)

    async def get_fee_stats(self) -> InvoiceFeeStats:
        """Get invoice fee statistics"""
        response = await self._client.get("/api/invoices/fees", authenticated=True)
        return InvoiceFeeStats.model_validate(response.get("data", response))
