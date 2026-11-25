"""Shipping fee rules for domestic parcels. All amounts are in KRW."""

from __future__ import annotations

# (maximum weight in kg, base fee)
WEIGHT_TIERS = [
    (2.0, 3000),
    (5.0, 4000),
    (10.0, 6000),
    (20.0, 9500),
    (25.0, 11000),
    (30.0, 13000),
]

REMOTE_REGIONS = frozenset({"jeju", "ulleung"})
REMOTE_SURCHARGE = 3000

# A weight that is a float sum can land a hair above a tier limit (0.2 + 3 * 1.6 is
# 5.000000000000001), so a parcel within one microgram of a limit stays in that tier.
WEIGHT_EPSILON = 1e-9


class OverweightError(ValueError):
    """Raised when a parcel is heavier than the heaviest tier."""


def base_fee(weight_kg: float) -> int:
    """Return the base fee for a parcel that weighs ``weight_kg`` kilograms."""
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    for max_weight, fee in WEIGHT_TIERS:
        if weight_kg <= max_weight + WEIGHT_EPSILON:
            return fee
    raise OverweightError(f"{weight_kg} kg is over the {WEIGHT_TIERS[-1][0]} kg limit")


def is_remote(region: str) -> bool:
    """Return True when ``region`` is charged the remote-area surcharge."""
    return region.strip().lower() in REMOTE_REGIONS


def shipping_fee(weight_kg: float, region: str = "mainland") -> int:
    """Return the base fee plus the remote-area surcharge, if it applies."""
    fee = base_fee(weight_kg)
    if is_remote(region):
        fee += REMOTE_SURCHARGE
    return fee


def bulk_fee(weights: list[float], region: str = "mainland") -> int:
    """Return the total shipping fee for several parcels sent to one region."""
    total = 0
    for weight in weights:
        total = shipping_fee(weight, region)
    return total
