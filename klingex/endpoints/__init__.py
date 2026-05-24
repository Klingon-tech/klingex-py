"""KlingEx API endpoints."""

from klingex.endpoints.markets import MarketsEndpoint, AsyncMarketsEndpoint
from klingex.endpoints.orders import OrdersEndpoint, AsyncOrdersEndpoint
from klingex.endpoints.wallet import WalletEndpoint, AsyncWalletEndpoint
from klingex.endpoints.invoices import InvoicesEndpoint, AsyncInvoicesEndpoint
from klingex.endpoints.withdrawals import WithdrawalsEndpoint, AsyncWithdrawalsEndpoint
from klingex.endpoints.pools import PoolsEndpoint, AsyncPoolsEndpoint
from klingex.endpoints.mining_pool import MiningPoolEndpoint, AsyncMiningPoolEndpoint
from klingex.endpoints.gift_codes import GiftCodesEndpoint, AsyncGiftCodesEndpoint

__all__ = [
    "MarketsEndpoint",
    "AsyncMarketsEndpoint",
    "OrdersEndpoint",
    "AsyncOrdersEndpoint",
    "WalletEndpoint",
    "AsyncWalletEndpoint",
    "InvoicesEndpoint",
    "AsyncInvoicesEndpoint",
    "WithdrawalsEndpoint",
    "AsyncWithdrawalsEndpoint",
    "PoolsEndpoint",
    "AsyncPoolsEndpoint",
    "MiningPoolEndpoint",
    "AsyncMiningPoolEndpoint",
    "GiftCodesEndpoint",
    "AsyncGiftCodesEndpoint",
]
