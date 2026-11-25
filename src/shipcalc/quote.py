"""Order quotes: item subtotal, coupon discount, shipping fee and validity date."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from shipcalc.rates import base_fee, shipping_fee

FREE_SHIPPING_MIN = 50000
SAVE10_MAX_DISCOUNT = 5000
VALID_DAYS = 7


@dataclass(frozen=True)
class Item:
    """One order line. ``unit_price`` is in KRW and ``weight_kg`` is the weight of one unit."""

    name: str
    unit_price: int
    quantity: int
    weight_kg: float


@dataclass(frozen=True)
class Quote:
    """A priced order. All amounts are in KRW."""

    subtotal: int
    discount: int
    shipping: int
    total: int
    valid_until: date


def _check_item(item: Item) -> None:
    if item.quantity < 1:
        raise ValueError(f"{item.name}: quantity must be at least 1")
    if item.unit_price < 0:
        raise ValueError(f"{item.name}: unit price must not be negative")
    if item.weight_kg <= 0:
        raise ValueError(f"{item.name}: weight must be positive")


def _coupon_discount(subtotal: int, coupon: str | None) -> int:
    """Return the amount that ``coupon`` takes off ``subtotal``.

    ``SAVE10`` is 10% of the subtotal, rounded down to a multiple of 10 KRW and never
    more than 5,000. ``FREESHIP`` only changes the shipping fee. Codes are matched
    exactly as given, and an unknown code raises ``ValueError``.
    """
    if coupon is None or coupon == "FREESHIP":
        return 0
    if coupon == "SAVE10":
        return min(subtotal // 10, SAVE10_MAX_DISCOUNT)
    raise ValueError(f"unknown coupon: {coupon!r}")


def quote(
    items: Iterable[Item],
    region: str = "mainland",
    coupon: str | None = None,
    today: date | None = None,
) -> Quote:
    """Price an order. All items ship together as one parcel.

    The base shipping fee is waived by the ``FREESHIP`` coupon and when the subtotal
    after the discount is 50,000 or more. The remote-area surcharge is still charged in
    both cases. The quote is valid for 7 days from ``today``, which defaults to the
    current date in UTC.
    """
    items = list(items)
    if not items:
        raise ValueError("an order needs at least one item")
    for item in items:
        _check_item(item)

    subtotal = sum(item.unit_price * item.quantity for item in items)
    weight = sum(item.weight_kg * item.quantity for item in items)
    discount = _coupon_discount(subtotal, coupon)

    base = base_fee(weight)
    shipping = shipping_fee(weight, region)
    if coupon == "FREESHIP":
        shipping -= base
    if subtotal - discount >= FREE_SHIPPING_MIN:
        shipping -= base

    if today is None:
        today = datetime.utcnow().date()
    return Quote(
        subtotal=subtotal,
        discount=discount,
        shipping=shipping,
        total=subtotal - discount + shipping,
        valid_until=today + timedelta(days=VALID_DAYS),
    )
