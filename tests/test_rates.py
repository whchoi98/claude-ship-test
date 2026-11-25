import pytest

from shipcalc import OverweightError, base_fee, bulk_fee, shipping_fee


@pytest.mark.parametrize(
    ("weight", "fee"),
    [
        (0.1, 3000),
        (2.0, 3000),
        (2.1, 4000),
        (5.0, 4000),
        (10.0, 6000),
        (10.5, 9500),
        (20.0, 9500),
        (20.1, 11000),
        (25.0, 11000),
        (25.5, 13000),
        (30.0, 13000),
    ],
)
def test_base_fee_by_tier(weight, fee):
    assert base_fee(weight) == fee


@pytest.mark.parametrize("weight", [0, -1.5])
def test_base_fee_rejects_non_positive_weight(weight):
    with pytest.raises(ValueError, match="positive"):
        base_fee(weight)


def test_base_fee_rejects_overweight_parcel():
    with pytest.raises(OverweightError):
        base_fee(30.1)


def test_base_fee_keeps_a_float_sum_on_a_tier_limit_in_that_tier():
    # 0.2 + 3 * 1.6 is 5 kg, but the float sum is 5.000000000000001
    assert base_fee(0.2 + 3 * 1.6) == 4000


def test_base_fee_rejects_a_parcel_just_over_the_limit():
    with pytest.raises(OverweightError):
        base_fee(30.0000004)


def test_shipping_fee_mainland_has_no_surcharge():
    assert shipping_fee(1.0) == 3000


@pytest.mark.parametrize("region", ["jeju", "Jeju", " ulleung "])
def test_shipping_fee_adds_remote_surcharge(region):
    assert shipping_fee(1.0, region) == 6000


def test_bulk_fee_for_one_parcel():
    assert bulk_fee([1.0]) == 3000
    assert bulk_fee([1.0], "jeju") == 6000
