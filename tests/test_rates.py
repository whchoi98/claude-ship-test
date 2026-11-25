import pytest

from shipcalc import OverweightError, base_fee, shipping_fee


@pytest.mark.parametrize(
    ("weight", "fee"),
    [
        (0.1, 3000),
        (2.0, 3000),
        (2.1, 4000),
        (5.0, 4000),
        (10.0, 6000),
        (10.5, 9000),
        (20.0, 9000),
        (20.5, 13000),
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


def test_shipping_fee_mainland_has_no_surcharge():
    assert shipping_fee(1.0) == 3000


@pytest.mark.parametrize("region", ["jeju", "Jeju", " ulleung "])
def test_shipping_fee_adds_remote_surcharge(region):
    assert shipping_fee(1.0, region) == 6000
