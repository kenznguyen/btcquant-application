"""Consumer-side contract for T1 BTCUSDT orderbook snapshots."""

from .contract import OrderbookSnapshot
from .errors import ContractError, ErrorCode
from .validation import validate_payload

__all__ = ["ContractError", "ErrorCode", "OrderbookSnapshot", "validate_payload"]
