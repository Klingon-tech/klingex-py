"""
KlingEx SDK Types and Models
"""

from enum import Enum
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# Enums
class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


# Market Models
class Market(BaseModel):
    """Trading market/pair"""
    id: int
    base_asset_id: int
    quote_asset_id: int
    min_trade_amount: str
    max_trade_amount: str
    tick_size: str
    step_size: str
    maker_fee_rate: str
    taker_fee_rate: str
    price_decimals: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    base_asset_symbol: str
    base_asset_name: str
    quote_asset_symbol: str
    quote_asset_name: str
    volume_24h: str
    priceChange24h: str
    last_price: str
    base_decimals: int
    quote_decimals: int
    volume_24h_human: str

    @property
    def symbol(self) -> str:
        """Returns trading pair symbol like BTC-USDT"""
        return f"{self.base_asset_symbol}-{self.quote_asset_symbol}"


class Asset(BaseModel):
    """Cryptocurrency asset"""
    symbol: str
    name: str
    decimals: int
    is_crypto: bool
    chain_type: str
    chain_id: Optional[int] = None
    evm_network: Optional[str] = None
    contract_address: Optional[str] = None
    is_active: bool
    withdrawal_enabled: bool
    website: Optional[str] = None
    twitter_url: Optional[str] = None
    discord_url: Optional[str] = None
    telegram_url: Optional[str] = None
    description: Optional[str] = None


class Ticker(BaseModel):
    """Market ticker data (CMC/CoinGecko format)"""
    ticker_id: str
    base_currency: str
    target_currency: str
    last_price: str
    base_volume: str
    target_volume: str
    bid: str
    ask: str
    high: str
    low: str


class OrderBook(BaseModel):
    """Orderbook snapshot"""
    trading_pair_id: int
    base_symbol: str
    quote_symbol: str
    bids: List[List[str]]  # [[price, amount], ...]
    asks: List[List[str]]  # [[price, amount], ...]


class OHLCV(BaseModel):
    """Candlestick/OHLCV data"""
    time_bucket: datetime
    open_price: str
    high_price: str
    low_price: str
    close_price: str
    volume: str
    number_of_trades: int


# Order Models
class Order(BaseModel):
    """Order details"""
    id: str
    trading_pair_id: int
    side: str
    type: str
    price: str
    amount: str
    filled_amount: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderResponse(BaseModel):
    """Order submission response"""
    message: str
    order_id: str


class CancelOrderResponse(BaseModel):
    """Cancel order response"""
    message: str
    released_balance: Optional[str] = None


# Wallet Models
class Balance(BaseModel):
    """Wallet balance"""
    id: int
    symbol: str
    name: str
    decimals: int
    balance: str
    locked_balance: str
    wallet_id: Optional[str] = None
    deposit_address: Optional[str] = None
    min_deposit: Optional[str] = None
    min_withdrawal: Optional[str] = None
    withdrawal_fee: Optional[str] = None

    @property
    def available(self) -> str:
        """Returns available balance (total - locked)"""
        return str(int(self.balance) - int(self.locked_balance))

    @property
    def total(self) -> str:
        """Returns total balance"""
        return self.balance


# Invoice Models
class InvoiceDenomination(BaseModel):
    """Invoice denomination"""
    type: str = "crypto"
    currency: str
    amount: str
    decimals: Optional[int] = None


class PaymentOption(BaseModel):
    """Invoice payment option"""
    asset_id: int
    symbol: str
    name: str
    chain_type: str
    address: str
    expected_amount: str
    exchange_rate: str
    qr_code_data: Optional[str] = None


class InvoicePayment(BaseModel):
    """Invoice payment record"""
    id: str
    asset_id: int
    symbol: str
    amount: str
    tx_hash: Optional[str] = None
    status: str
    confirmations: Optional[int] = None
    confirmations_required: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime


class Invoice(BaseModel):
    """Payment invoice"""
    id: str
    external_id: Optional[str] = None
    status: str
    denomination: Optional[InvoiceDenomination] = None
    # For list view (flat fields)
    denomination_type: Optional[str] = None
    denomination_currency: Optional[str] = None
    amount: Optional[str] = None
    payment_options: Optional[List[PaymentOption]] = None
    payments: Optional[List[InvoicePayment]] = None
    fee_rate_bps: Optional[int] = None
    fee_rate_percent: Optional[str] = None
    total_received: Optional[str] = None
    fee_amount: Optional[str] = None
    net_amount: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    buyer_email: Optional[str] = None
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    payment_page_url: Optional[str] = None


class InvoiceListResponse(BaseModel):
    """Invoice list response"""
    invoices: List[Invoice]
    total_count: int
    page: int
    page_size: int


class InvoiceFeeStats(BaseModel):
    """Invoice fee statistics"""
    current_fee_rate_bps: int
    current_fee_rate_percent: str
    paid_invoice_count: int
    total_fees_collected: str
    total_net_amount: str


__all__ = [
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Asset",
    "Market",
    "Ticker",
    "OrderBook",
    "OHLCV",
    "Order",
    "OrderResponse",
    "CancelOrderResponse",
    "Balance",
    "InvoiceDenomination",
    "PaymentOption",
    "InvoicePayment",
    "Invoice",
    "InvoiceListResponse",
    "InvoiceFeeStats",
]
