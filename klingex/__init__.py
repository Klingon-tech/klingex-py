"""KlingEx Python SDK - Official Python client for KlingEx Exchange API."""

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
    AssetInfo,
    Market,
    MarketInfo,
    SparklinePoint,
    MarketSparklinesResponse,
    Ticker,
    OrderBook,
    OHLCV,
    # Orders
    Order,
    OrderResponse,
    CancelOrderResponse,
    CancelAllOrdersResponse,
    OrderHistory,
    OrdersHistoryResponse,
    # Wallet
    Balance,
    WalletSystemStatus,
    WalletStatusCounts,
    WalletChainGroup,
    AssetSyncRow,
    AssetSyncStatus,
    AssetSyncInfo,
    # Withdrawals
    WithdrawalSubmitResponse,
    # Pools
    Pool,
    PoolDetail,
    LPPosition,
    PositionHistorySnapshot,
    PositionHistoryResponse,
    AddLiquidityResult,
    RemoveLiquidityResult,
    # Mining pool
    MiningPoolConfig,
    MiningBlock,
    MiningBlocksResponse,
    MiningStats,
    MiningStatsCurrent,
    MiningStatsSnapshot,
    MiningLeaderboard,
    MiningLeaderboardEntry,
    MiningWorker,
    MiningWorkersResponse,
    MiningReward,
    MiningRewardsResponse,
    MiningPayout,
    MiningPayoutsResponse,
    # Gift codes
    GiftCodeResponse,
    BulkGiftCodeResponse,
    # Invoices
    Invoice,
    InvoiceListResponse,
    InvoiceFeeStats,
    InvoiceStatusResponse,
    PublicInvoice,
    InvoiceDenomination,
    PaymentOption,
    InvoicePayment,
)

__version__ = "1.2.0"

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
    # Markets / assets
    "Asset",
    "AssetInfo",
    "Market",
    "MarketInfo",
    "SparklinePoint",
    "MarketSparklinesResponse",
    "Ticker",
    "OrderBook",
    "OHLCV",
    # Orders
    "Order",
    "OrderResponse",
    "CancelOrderResponse",
    "CancelAllOrdersResponse",
    "OrderHistory",
    "OrdersHistoryResponse",
    # Wallet
    "Balance",
    "WalletSystemStatus",
    "WalletStatusCounts",
    "WalletChainGroup",
    "AssetSyncRow",
    "AssetSyncStatus",
    "AssetSyncInfo",
    # Withdrawals
    "WithdrawalSubmitResponse",
    # Pools
    "Pool",
    "PoolDetail",
    "LPPosition",
    "PositionHistorySnapshot",
    "PositionHistoryResponse",
    "AddLiquidityResult",
    "RemoveLiquidityResult",
    # Mining pool
    "MiningPoolConfig",
    "MiningBlock",
    "MiningBlocksResponse",
    "MiningStats",
    "MiningStatsCurrent",
    "MiningStatsSnapshot",
    "MiningLeaderboard",
    "MiningLeaderboardEntry",
    "MiningWorker",
    "MiningWorkersResponse",
    "MiningReward",
    "MiningRewardsResponse",
    "MiningPayout",
    "MiningPayoutsResponse",
    # Gift codes
    "GiftCodeResponse",
    "BulkGiftCodeResponse",
    # Invoices
    "Invoice",
    "InvoiceListResponse",
    "InvoiceFeeStats",
    "InvoiceStatusResponse",
    "PublicInvoice",
    "InvoiceDenomination",
    "PaymentOption",
    "InvoicePayment",
]
