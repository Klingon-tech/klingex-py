"""
Invoices Endpoint - Payment processing
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from klingex.types import Invoice, InvoicePayment

if TYPE_CHECKING:
    from klingex.http import HttpClient, AsyncHttpClient


class InvoicesEndpoint:
    """Invoice/payment endpoints (authenticated)"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def create_invoice(
        self,
        asset_id: str,
        amount: str,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        redirect_url: Optional[str] = None,
        expires_in_minutes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Invoice:
        """Create a payment invoice

        Args:
            asset_id: Asset to accept payment in
            amount: Payment amount
            description: Optional invoice description
            callback_url: URL to receive payment notifications
            redirect_url: URL to redirect user after payment
            expires_in_minutes: Invoice expiration time in minutes
            metadata: Optional custom metadata
        """
        data: Dict[str, Any] = {
            "assetId": asset_id,
            "amount": amount,
        }
        if description:
            data["description"] = description
        if callback_url:
            data["callbackUrl"] = callback_url
        if redirect_url:
            data["redirectUrl"] = redirect_url
        if expires_in_minutes:
            data["expiresInMinutes"] = expires_in_minutes
        if metadata:
            data["metadata"] = metadata

        result = self._client.post("/api/invoices", data=data, authenticated=True)
        return Invoice.model_validate(result)

    def get_invoice(self, invoice_id: str) -> Invoice:
        """Get an invoice by ID

        Args:
            invoice_id: Invoice ID
        """
        data = self._client.get(f"/api/invoices/{invoice_id}", authenticated=True)
        return Invoice.model_validate(data)

    def get_invoices(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Invoice]:
        """Get invoice history

        Args:
            status: Optional status to filter by (pending, paid, expired, cancelled)
            limit: Maximum number of invoices to return
            offset: Pagination offset
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if status:
            params["status"] = status

        data = self._client.get("/api/invoices", params=params, authenticated=True)
        invoices_data = data.get("invoices", data) if isinstance(data, dict) else data
        return [Invoice.model_validate(i) for i in invoices_data]

    def cancel_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Cancel an invoice

        Args:
            invoice_id: Invoice ID to cancel
        """
        return self._client.delete(f"/api/invoices/{invoice_id}", authenticated=True)

    def get_invoice_payments(self, invoice_id: str) -> List[InvoicePayment]:
        """Get payments for an invoice

        Args:
            invoice_id: Invoice ID
        """
        data = self._client.get(f"/api/invoices/{invoice_id}/payments", authenticated=True)
        payments_data = data.get("payments", data) if isinstance(data, dict) else data
        return [InvoicePayment.model_validate(p) for p in payments_data]


class AsyncInvoicesEndpoint:
    """Async invoice/payment endpoints (authenticated)"""

    def __init__(self, client: "AsyncHttpClient"):
        self._client = client

    async def create_invoice(
        self,
        asset_id: str,
        amount: str,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        redirect_url: Optional[str] = None,
        expires_in_minutes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Invoice:
        """Create a payment invoice"""
        data: Dict[str, Any] = {
            "assetId": asset_id,
            "amount": amount,
        }
        if description:
            data["description"] = description
        if callback_url:
            data["callbackUrl"] = callback_url
        if redirect_url:
            data["redirectUrl"] = redirect_url
        if expires_in_minutes:
            data["expiresInMinutes"] = expires_in_minutes
        if metadata:
            data["metadata"] = metadata

        result = await self._client.post("/api/invoices", data=data, authenticated=True)
        return Invoice.model_validate(result)

    async def get_invoice(self, invoice_id: str) -> Invoice:
        """Get an invoice by ID"""
        data = await self._client.get(f"/api/invoices/{invoice_id}", authenticated=True)
        return Invoice.model_validate(data)

    async def get_invoices(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Invoice]:
        """Get invoice history"""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if status:
            params["status"] = status

        data = await self._client.get("/api/invoices", params=params, authenticated=True)
        invoices_data = data.get("invoices", data) if isinstance(data, dict) else data
        return [Invoice.model_validate(i) for i in invoices_data]

    async def cancel_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Cancel an invoice"""
        return await self._client.delete(f"/api/invoices/{invoice_id}", authenticated=True)

    async def get_invoice_payments(self, invoice_id: str) -> List[InvoicePayment]:
        """Get payments for an invoice"""
        data = await self._client.get(f"/api/invoices/{invoice_id}/payments", authenticated=True)
        payments_data = data.get("payments", data) if isinstance(data, dict) else data
        return [InvoicePayment.model_validate(p) for p in payments_data]
