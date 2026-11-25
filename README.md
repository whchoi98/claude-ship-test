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

- A parcel heavier than 25 kg is not accepted.
- Remote regions (`jeju`, `ulleung`) add 3,000 to the base fee.

## Usage

```python
from shipcalc import shipping_fee

shipping_fee(1.5)           # 3000
shipping_fee(7, "jeju")     # 9000
```

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest -q
```

The same three checks run in GitHub Actions on Python 3.9 and 3.12.
