# shipcalc

A small parcel shipping fee calculator. It is a sample project for trying out the
Claude Code `/ship` command, so the code is short on purpose.

## Rules

All amounts are in KRW.

| Weight | Base fee |
|---|---|
| up to 2 kg | 3,000 |
| up to 5 kg | 4,000 |
| up to 10 kg | 6,000 |
| up to 20 kg | 9,500 |
| up to 25 kg | 11,000 |
| up to 30 kg | 13,000 |

- A parcel heavier than 30 kg is not accepted.
- Remote regions (`jeju`, `ulleung`) add 3,000 to the base fee.

## Usage

```python
from shipcalc import shipping_fee

shipping_fee(1.5)           # 3000
shipping_fee(7, "jeju")     # 9000
```

## Order quotes

`quote()` prices a whole order: the item subtotal, a coupon discount, the shipping fee
and the date until which the quote is valid.

- (a) The subtotal is the sum of `unit_price × quantity`. The parcel weight is the sum of
  `weight_kg × quantity`; all items ship as one parcel.
- (b) An empty item list, a quantity below 1, a negative price, or a non-positive weight
  raises `ValueError`.
- (c) Coupon codes are matched without regard to case or surrounding whitespace
  (`save10` and ` SAVE10 ` both count as `SAVE10`).
  - `SAVE10`: 10% off the subtotal, rounded down to a multiple of 10 KRW, and never more
    than 5,000.
  - `FREESHIP`: the base shipping fee is waived.
  - Any other code raises `ValueError`.
- (d) Free shipping: when the subtotal after the discount is 50,000 or more, the base
  shipping fee is waived.
- (e) The remote-area surcharge (3,000) is always charged for remote regions, also when
  the base fee is waived.
- (f) The total is the subtotal minus the discount plus the shipping fee.
- (g) A quote is valid until the quote date plus 7 days. The quote date is `today` when
  given, otherwise the current date in UTC.

```python
import datetime

from shipcalc import Item, quote

items = [
    Item("keyboard", unit_price=45000, quantity=1, weight_kg=0.9),
    Item("mouse pad", unit_price=8000, quantity=2, weight_kg=0.3),
]
q = quote(items, region="jeju", coupon="SAVE10", today=datetime.date(2026, 3, 10))

q.subtotal     # 61000
q.discount     # 5000
q.shipping     # 3000 (base fee waived, remote surcharge only)
q.total        # 59000
q.valid_until  # datetime.date(2026, 3, 17)
```

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest -q
```

The same three checks run in GitHub Actions on Python 3.9 and 3.12.
