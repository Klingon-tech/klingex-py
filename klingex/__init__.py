"""
KlingEx Python SDK - Official Python client for KlingEx Exchange API
"""

from klingex.client import KlingEx, AsyncKlingEx
from klingex.http import KlingExError, AuthenticationError, RateLimitError, ValidationError
from klingex.websocket import KlingExWebSocket
from klingex.types import (
    # Common
    OrderSide,
    OrderType,
    OrderStatus,
    TimeInForce,
    # Market data
    Asset,
    Market,
    Ticker,
    OrderBookEntry,
    OrderBook,
    OHLCV,
    Trade,
    # Orders
    Order,
    OrderSubmission,
    OrderResponse,
    # Wallet
    Balance,
    Deposit,
    Withdrawal,
    WithdrawalRequest,
    DepositAddress,
    # Invoices
    Invoice,
    InvoicePayment,
)

__version__ = "1.0.0"
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
    "TimeInForce",
    # Types
    "Asset",
    "Market",
    "Ticker",
    "OrderBookEntry",
    "OrderBook",
    "OHLCV",
    "Trade",
    "Order",
    "OrderSubmission",
    "OrderResponse",
    "Balance",
    "Deposit",
    "Withdrawal",
    "WithdrawalRequest",
    "DepositAddress",
    "Invoice",
    "InvoicePayment",
]
