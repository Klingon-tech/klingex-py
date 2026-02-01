"""
KlingEx SDK Types and Models
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# Enums
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


class TimeInForce(str, Enum):
    GTC = "gtc"  # Good Till Cancelled
    IOC = "ioc"  # Immediate Or Cancel
    FOK = "fok"  # Fill Or Kill


# Base Models
class Asset(BaseModel):
    """Cryptocurrency asset"""
    id: str
    symbol: str
    name: str
    decimals: int
    chain: Optional[str] = None
    contract_address: Optional[str] = Field(None, alias="contractAddress")
    is_active: bool = Field(True, alias="isActive")
    min_withdrawal: Optional[str] = Field(None, alias="minWithdrawal")
    withdrawal_fee: Optional[str] = Field(None, alias="withdrawalFee")

    class Config:
        populate_by_name = True


class Market(BaseModel):
    """Trading market/pair"""
    id: str
    symbol: str
    base_asset: str = Field(..., alias="baseAsset")
    quote_asset: str = Field(..., alias="quoteAsset")
    base_decimals: int = Field(..., alias="baseDecimals")
    quote_decimals: int = Field(..., alias="quoteDecimals")
    min_order_size: Optional[str] = Field(None, alias="minOrderSize")
    max_order_size: Optional[str] = Field(None, alias="maxOrderSize")
    price_tick: Optional[str] = Field(None, alias="priceTick")
    is_active: bool = Field(True, alias="isActive")

    class Config:
        populate_by_name = True


class Ticker(BaseModel):
    """Market ticker data"""
    market_id: str = Field(..., alias="marketId")
    symbol: str
    last_price: str = Field(..., alias="lastPrice")
    bid: Optional[str] = None
    ask: Optional[str] = None
    high_24h: Optional[str] = Field(None, alias="high24h")
    low_24h: Optional[str] = Field(None, alias="low24h")
    volume_24h: Optional[str] = Field(None, alias="volume24h")
    change_24h: Optional[str] = Field(None, alias="change24h")
    change_percent_24h: Optional[str] = Field(None, alias="changePercent24h")
    timestamp: Optional[datetime] = None

    class Config:
        populate_by_name = True


class OrderBookEntry(BaseModel):
    """Single orderbook entry"""
    price: str
    quantity: str


class OrderBook(BaseModel):
    """Orderbook snapshot"""
    market_id: str = Field(..., alias="marketId")
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: Optional[datetime] = None

    class Config:
        populate_by_name = True


class OHLCV(BaseModel):
    """Candlestick/OHLCV data"""
    timestamp: datetime
    open: str
    high: str
    low: str
    close: str
    volume: str


class Trade(BaseModel):
    """Executed trade"""
    id: str
    market_id: str = Field(..., alias="marketId")
    price: str
    quantity: str
    side: OrderSide
    timestamp: datetime
    is_maker: Optional[bool] = Field(None, alias="isMaker")

    class Config:
        populate_by_name = True


# Order Models
class Order(BaseModel):
    """Order details"""
    id: str
    market_id: str = Field(..., alias="marketId")
    side: OrderSide
    type: OrderType
    status: OrderStatus
    price: Optional[str] = None
    quantity: str
    filled_quantity: str = Field("0", alias="filledQuantity")
    remaining_quantity: Optional[str] = Field(None, alias="remainingQuantity")
    average_price: Optional[str] = Field(None, alias="averagePrice")
    time_in_force: Optional[TimeInForce] = Field(None, alias="timeInForce")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True


class OrderSubmission(BaseModel):
    """Order submission request"""
    market_id: str = Field(..., alias="marketId")
    side: OrderSide
    type: OrderType
    quantity: str
    price: Optional[str] = None
    time_in_force: Optional[TimeInForce] = Field(None, alias="timeInForce")
    raw_values: bool = Field(False, alias="rawValues")

    class Config:
        populate_by_name = True


class OrderResponse(BaseModel):
    """Order submission response"""
    order_id: str = Field(..., alias="orderId")
    status: str
    message: Optional[str] = None

    class Config:
        populate_by_name = True


# Wallet Models
class Balance(BaseModel):
    """Wallet balance"""
    asset_id: str = Field(..., alias="assetId")
    symbol: str
    available: str
    locked: str
    total: str

    class Config:
        populate_by_name = True


class Deposit(BaseModel):
    """Deposit record"""
    id: str
    asset_id: str = Field(..., alias="assetId")
    amount: str
    status: str
    tx_hash: Optional[str] = Field(None, alias="txHash")
    confirmations: Optional[int] = None
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class Withdrawal(BaseModel):
    """Withdrawal record"""
    id: str
    asset_id: str = Field(..., alias="assetId")
    amount: str
    fee: Optional[str] = None
    address: str
    status: str
    tx_hash: Optional[str] = Field(None, alias="txHash")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class WithdrawalRequest(BaseModel):
    """Withdrawal request"""
    asset_id: str = Field(..., alias="assetId")
    amount: str
    address: str
    memo: Optional[str] = None
    two_fa_code: Optional[str] = Field(None, alias="twoFaCode")

    class Config:
        populate_by_name = True


class DepositAddress(BaseModel):
    """Deposit address"""
    asset_id: str = Field(..., alias="assetId")
    address: str
    memo: Optional[str] = None
    chain: Optional[str] = None

    class Config:
        populate_by_name = True


# Invoice Models
class Invoice(BaseModel):
    """Payment invoice"""
    id: str
    merchant_id: str = Field(..., alias="merchantId")
    asset_id: str = Field(..., alias="assetId")
    amount: str
    status: str
    description: Optional[str] = None
    callback_url: Optional[str] = Field(None, alias="callbackUrl")
    redirect_url: Optional[str] = Field(None, alias="redirectUrl")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    created_at: datetime = Field(..., alias="createdAt")
    payment_address: Optional[str] = Field(None, alias="paymentAddress")

    class Config:
        populate_by_name = True


class InvoicePayment(BaseModel):
    """Invoice payment record"""
    id: str
    invoice_id: str = Field(..., alias="invoiceId")
    amount: str
    tx_hash: Optional[str] = Field(None, alias="txHash")
    status: str
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


__all__ = [
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "TimeInForce",
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
