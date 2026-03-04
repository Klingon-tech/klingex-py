"""
KlingEx Python SDK - Official Python client for KlingEx Exchange API
"""

from klingex.client import KlingEx, AsyncKlingEx
from klingex.http import KlingExError, AuthenticationError, RateLimitError, ValidationError
from klingex.websocket import KlingExWebSocket
from klingex.types import (
    # Enums
    OrderSide,
    OrderType,
    OrderStatus,
    # Market data
    Asset,
    Market,
    Ticker,
    OrderBook,
    OHLCV,
    # Orders
    Order,
    OrderResponse,
    CancelOrderResponse,
    # Wallet
    Balance,
    # Invoices
    Invoice,
    InvoiceListResponse,
    InvoiceFeeStats,
    InvoiceDenomination,
    PaymentOption,
    InvoicePayment,
)

__version__ = "1.1.0"
__all__ = [
    # Main classes
    "KlingEx",
    "AsyncKlingEx",
    "KlingExWebSocket",
    # Errors
    "KlingExError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    # Enums
    "OrderSide",
    "OrderType",
    "OrderStatus",
    # Types
    "Asset",
    "Market",
    "Ticker",
    "OrderBook",
    "OHLCV",
    "Order",
    "OrderResponse",
    "CancelOrderResponse",
    "Balance",
    "Invoice",
    "InvoiceListResponse",
    "InvoiceFeeStats",
    "InvoiceDenomination",
    "PaymentOption",
    "InvoicePayment",
]
