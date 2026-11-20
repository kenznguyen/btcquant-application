"""Explicit local initialization of the paper ledger; never sends an order."""

import argparse
import json
from pathlib import Path

from paper_execution.database_paths import PaperDatabasePathError, resolve_paper_db_path
from paper_execution.ledger import PaperLedger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="SQLite database path")
    parser.add_argument("--max-position-base", default="0.01")
    parser.add_argument("--fee-rate", default="0.0005")
    parser.add_argument("--max-spread-bps", default="50")
    args = parser.parse_args()
    try:
        configured_path = resolve_paper_db_path()
        requested_path = Path(args.db).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError, PaperDatabasePathError) as error:
        parser.error(str(error))
    if requested_path != configured_path:
        parser.error("--db must resolve to the configured PAPER_DB path")
    ledger = PaperLedger(str(configured_path), max_position_base=args.max_position_base,
                         fee_rate=args.fee_rate, max_spread_bps=args.max_spread_bps)
    print(json.dumps(ledger.snapshot(), allow_nan=False))


if __name__ == "__main__":
    main()
