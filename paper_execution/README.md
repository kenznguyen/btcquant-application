# Paper execution — tầng 3

`PaperLedger` mô phỏng lệnh limit BTCUSDT USDⓈ-M trên độ sâu đang hiển thị từ
Hummingbot. Module chỉ dùng SQLite/Decimal và **không có HTTP client, API key sàn
hoặc hàm gửi lệnh thật**. `liveTradingSupported` luôn là `false`.

```python
from paper_execution.ledger import PaperLedger
from paper_execution.risk_contract import provision_account_risk_contract

db_path = ".data/paper/paper-ledger.sqlite3"
# MARKET_DATA_DB remains the separate, T0-owned canonical candle database.
# Set PAPER_DB to this path before invoking the Paper API or initializer.
provision_account_risk_contract(
    db_path,
    {
        "maxDrawdownPct": "20",
        "maxDailyLossUsdt": "10",
        "maxExposureUsdt": "1000",
    },
    source="OPERATOR_APPROVED_CONFIGURATION",
    recorded_at_ms=now_ms,
)
ledger = PaperLedger(db_path, max_position_base="0.01", fee_rate="0.0005")
result = ledger.submit(validated_paper_intent, validated_orderbook_snapshot, now_ms)
state = ledger.snapshot()
```

Khởi tạo local là thao tác riêng, không thực hiện trong HTTP GET. CLI bắt buộc nhận
`PAPER_DB`; `--db` phải resolve đúng về `PAPER_DB` và bị từ chối nếu trùng/alias
`MARKET_DATA_DB` hoặc `T0_FEEDER_LEASE_DB`. API chỉ mở file Paper đã tồn tại; nó
không tự tạo file PAPER_DB thiếu. T0 Candle API tiếp tục đọc theo storage factory
và không tạo bảng Paper trong canonical SQLite:

```bash
PAPER_DB=.data/paper/paper-ledger.sqlite3 python3 -m paper_execution --db "$PAPER_DB"
```

CLI có tham số `--max-position-base`, `--fee-rate`, `--max-spread-bps`.
Risk limits thuộc một Account/Risk Contract được lưu và xác thực ở cấp account;
mọi Ledger dùng chung contract này, không truyền bộ giới hạn riêng theo strategy.
Provision lần đầu qua `provision_account_risk_contract`; lặp lại cùng cấu hình là
idempotent, cấu hình xung đột bị từ chối. Cập nhật phải dùng
`update_account_risk_contract` với `expected_contract_hash`, source và reason để
ghi audit. Thiếu contract sẽ chặn tăng exposure; contract sai hash/schema cũng
fail-closed. Client chỉ đọc dùng `read_snapshot(db_path)` (SQLite `mode=ro`),
không gọi constructor để tự tạo state. Đọc khi thiếu database/tables/state báo lỗi,
không tạo ledger rỗng.

Intent và snapshot theo [`pipeline/CONTRACTS.md`](../pipeline/CONTRACTS.md).
Tham số `targetPositionBase` là vị thế ròng mục tiêu có dấu, không phải khối lượng
lệnh mới: `+` là long và `-` là short. Ledger tính chênh lệch với vị thế hiện tại.
Lệnh mới bị từ chối nếu hệ thống pause, intent hết hạn, vượt giới hạn vị thế,
spread vượt ngưỡng cấu hình hoặc còn lệnh OPEN/PARTIALLY_FILLED chưa được hủy.
Các giới hạn này là cấu hình của mô phỏng, chưa phải chính sách được duyệt cho live.

Snapshot phải đúng nguồn Hummingbot/binance_perpetual/BTCUSDT, có hai phía hợp lệ,
không chéo, tối đa 20 mức/phía, không quá cũ (30 giây) hoặc trước đồng hồ máy chủ
quá xa (5 giây). Timestamp là lúc lấy snapshot, **không chứng nhận thời điểm sự
kiện cuối của sàn, hàng đợi khớp lệnh hoặc chuỗi cập nhật đã đồng bộ**.

## Mô hình khớp

- BUY tiêu thụ ask từ thấp lên cao, SELL tiêu thụ bid từ cao xuống thấp, chỉ trong
  giới hạn giá và không vượt khối lượng hiển thị.
- Phần chưa khớp ở trạng thái OPEN hoặc PARTIALLY_FILLED. Không có background fill
  hay giả định rằng lệnh limit chắc chắn sẽ được khớp trong tương lai.
- Đường MANUAL/legacy cũ giữ cơ chế snapshot đơn-lần. Với Dual Ledger, Core/AI
  và đường Legacy reduction theo dõi lượng đã khớp ở từng mức giá trong cùng snapshot.
  Mỗi transaction trừ cả Core/AI level reservations và Legacy consumptions trước khi
  tính lượng còn hiển thị; tổng fill không vượt depth của snapshot. Đây chỉ là mô hình
  paper trên snapshot, không chứng minh thanh khoản hoặc khả năng khớp lệnh thật.
- Phí bằng quote notional thực sự mô phỏng đã khớp nhân fee rate. Tính toán dùng
  Decimal với precision 80, không dùng float cho tiền trong ledger.
- Giá vốn/PnL được cập nhật theo từng fill ở từng mức giá, để fill đóng vị thế cũ
  và fill mở vị thế đảo chiều không bị gộp sai vào VWAP toàn lệnh. VWAP chỉ là giá
  trung bình hiển thị của order.
- `realizedPnlQuote` là PnL đã thực hiện **trước phí**. `feesQuote` gồm phí tất cả
  fill; `netRealizedPnlQuote` bằng realized trừ toàn bộ phí đó, gồm phí vào của vị
  thế còn mở. Không báo chỉ số này như equity, PnL toàn tài khoản hoặc lợi nhuận live.

## State và tính lặp

Các bảng `paper_*` được thêm vào cùng SQLite mà không thay bảng nến. Mỗi submit
claim intent ID, cập nhật vị thế/fill/phí và ghi audit trong một giao dịch SQLite
`BEGIN IMMEDIATE`; các tiến trình đồng thời không khớp trùng cùng một intent.
ID/payload giống nhau trả lệnh đã lưu; ID giống nhưng payload khác bị lỗi.
Sau cancel, submit lại cùng intent trả trạng thái CANCELED hiện có và không mở lại.
State lưu trên đĩa được kiểm tra tính hữu hạn của Decimal, dấu của phí, quan hệ
giữa vị thế/giá vốn và cờ pause trước khi đọc hoặc submit. State hỏng/mất row báo
`sqlite3.DatabaseError`; constructor không tự tái tạo row đã mất thành FLAT.

`set_paused(True, now_ms)` chặn intent mới, giữ các lệnh/vị thế đã có.
`cancel(order_id, now_ms)` chỉ hủy phần chưa khớp; không đảo ngược fill hoặc phí.
Pause/cancel không đồng nghĩa đóng vị thế. Ledger không cung cấp lệnh flatten tự
động hay nút bật live. Snapshot hiển thị tối đa 100 lệnh gần nhất.


## LEGACY_UNATTRIBUTED close-only reconciliation

Schema migration v2 adds `paper_legacy_book_consumptions` separately from the
Core/AI risk-reservation tables. Records reference the paper order, book snapshot,
side/price/consumed quantity, reconciliation ID and a `sha256:` digest. Database
constraints enforce the digest format and prevent updates/deletes of recorded
consumption evidence.

`reduce_legacy_unattributed(db_path, intent, book, now_ms, ...)` is a PAPER-only
module API for reducing or flattening an existing `LEGACY_UNATTRIBUTED` position.
It rejects increases and reversals, does not create Core/AI risk reservations, and
does not reassign ownership. A valid reduction remains permitted while the shared
Kill Switch is active. It uses `BEGIN IMMEDIATE` and records each filled book level
so subsequent Core/AI orders see only the remaining visible depth. The caller must
supply a reconciliation ID and a lowercase `sha256:` digest of the external
reconciliation evidence; format validation does not independently verify the
underlying evidence bytes.

This API is not an owner-reassignment mechanism, production migration command,
backtest, exchange adapter or live execution path. `ai_execution_enabled=false`
remains mandatory.


## Reservation expiry and restart recovery

Migration v3 adds nullable expires_at_ms to paper_risk_reservations and an expiry
index. New Core/AI orders persist validUntilMs in the order document and the same
admission-time deadline in their reservation. A pending or partial reservation
expires only after now_ms is later than validUntilMs; its order becomes EXPIRED and
only the unfilled remaining margin/notional is released. Filled position, PnL, fees
and consumed book depth are not rolled back.

Expiry is swept transactionally before a scoped Core/AI submit or cancel, so a
restart does not reset the deadline. Retrying the original intent returns the
persisted EXPIRED order. Read-only snapshots never perform expiry writes. Historical
active reservations with no trustworthy expiry timestamp remain active and continue
to block same-ledger replacement; they require explicit cancel/reconciliation rather
than an invented deadline.

## Kiểm chứng

```bash
python3 -m unittest paper_execution.test_ledger -v
```

Kiểm thử bao gồm persistence/restart, fill/partial fill, lệnh limit không chạm giá,
retry cùng ID, payload xung đột, pause/cancel, input sai/hết hạn, chống dùng lại
snapshot, phí/PnL khi giảm và đảo chiều vị thế, submit đồng thời. Các kiểm thử chỉ
dùng SQLite thật và dữ liệu fixture; chưa chứng nhận tính đúng với fill của sàn.


## Funding provenance v4 and verified account cutover v5

Migration v4 adds source and recorded timestamps to funding events and creates
append-only funding-coverage evidence. The API record_funding_event(...) is
idempotent by event ID, rejects payload conflicts, stores source/snapshot identity
and a lowercase SHA-256 digest, and prevents update/delete. Positive funding amounts
are costs; negative amounts are credits. If a historical funding amount is known
but its strategy owner is not, record it under LEGACY_UNATTRIBUTED, never Core or AI.
An existing funding row without source provenance is marked LEGACY_UNVERIFIED and
keeps account risk readiness blocked.

The API record_funding_coverage(...) records VERIFIED, UNKNOWN or DISABLED intervals.
UNKNOWN coverage is not interpreted as zero and demotes account risk readiness.
DISABLED is accepted only with PAPER_TEST_CONFIGURATION and a persisted
configuration version, snapshot identity and payload digest. Coverage metadata and
event hashes are provenance references; the ledger does not fetch or independently
re-hash external statement bytes.

Migration v5 adds one immutable paper_account_equity_cutovers record per account.
The API record_account_equity_cutover(...) requires contiguous funding coverage for
the declared reconciliation interval, fresh mark and closed-candle timestamps,
dataset identity, source/snapshot/hash/config provenance, and explicit expected
statement totals for capital, realized PnL, fees, funding and account equity. It
reconciles Core + AI + Legacy ledgers and legacy account adjustments, verifies
funding event totals against each ledger, and computes mark-to-market equity. Only
a successful cutover establishes HWM and the UTC daily baseline and sets risk
readiness.

Account snapshots and new exposure admissions require v4/v5 and a persisted
cutover. Any UNKNOWN funding interval overlapping the cutover window keeps
readiness false and blocks exposure increases, even if a stale readiness flag was
manually set. Valid reductions remain available under the existing shared-risk
policy. A cutover is one-time and immutable; a different second cutover requires a
separately reviewed reconciliation/reset procedure.

Both migrations are additive and execute only when a scoped Core/AI writer opens
an isolated test database. No persistent account database migration is implied.
