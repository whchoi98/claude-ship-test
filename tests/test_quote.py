import datetime

import pytest

from shipcalc import Item, OverweightError, Quote, quote

BOOK = Item("book", unit_price=12000, quantity=1, weight_kg=0.4)
MUGS = Item("mug", unit_price=4000, quantity=2, weight_kg=0.35)
DESK = Item("desk", unit_price=80000, quantity=1, weight_kg=18.0)


def test_quote_adds_up_items_and_shipping():
    result = quote([BOOK, MUGS], today=datetime.date(2026, 3, 10))
    assert result == Quote(
        subtotal=20000,
        discount=0,
        shipping=3000,
        total=23000,
        valid_until=datetime.date(2026, 3, 17),
    )


def test_valid_until_is_seven_days_after_the_quote_date():
    result = quote([BOOK], today=datetime.date(2026, 2, 25))
    assert result.valid_until == datetime.date(2026, 3, 4)


def test_items_ship_as_one_parcel():
    # 4 x 0.6 kg = 2.4 kg, which falls in the 5 kg tier
    result = quote([Item("jam", unit_price=5000, quantity=4, weight_kg=0.6)])
    assert result.subtotal == 20000
    assert result.shipping == 4000


@pytest.mark.parametrize(
    ("items", "shipping"),
    [
        # 0.2 + 3 x 1.6 is exactly 5 kg, but the float sum is 5.000000000000001
        ([Item("tea", 1000, 1, 0.2), Item("rice", 1000, 3, 1.6)], 4000),
        # 0.3 + 3 x 9.9 is exactly 30 kg, the heaviest parcel that is accepted
        ([Item("cable", 1000, 1, 0.3), Item("plate", 1000, 3, 9.9)], 13000),
    ],
)
def test_weight_on_a_tier_limit_stays_in_that_tier(items, shipping):
    assert quote(items).shipping == shipping


def test_very_light_item_is_priced_in_the_lowest_tier():
    # the summed weight must not shrink to zero on the way to the fee table
    assert quote([Item("seed", 1000, 1, 0.0000004)]).shipping == 3000


def test_parcel_just_over_the_weight_limit_is_rejected():
    with pytest.raises(OverweightError):
        quote([Item("anvil", 1000, 1, 30.0000004)])


def test_remote_region_adds_the_surcharge():
    assert quote([BOOK], region="Ulleung").shipping == 6000


def test_save10_takes_ten_percent_off():
    result = quote([BOOK, MUGS], coupon="SAVE10")
    assert result.discount == 2000
    assert result.total == 21000


def test_save10_discount_is_capped():
    result = quote([DESK], coupon="SAVE10")
    assert result.discount == 5000
    assert result.total == 75000


def test_save10_discount_is_rounded_down_to_ten_won():
    # 10% of 3,750 is 375, which rounds down to 370
    result = quote([Item("pen", unit_price=1250, quantity=3, weight_kg=0.1)], coupon="SAVE10")
    assert result.discount == 370
    assert result.total == 6380


def test_freeship_waives_the_base_fee():
    result = quote([BOOK], coupon="FREESHIP")
    assert result.discount == 0
    assert result.shipping == 0
    assert result.total == 12000


@pytest.mark.parametrize(("region", "shipping"), [("mainland", 0), ("jeju", 3000)])
def test_freeship_on_a_free_shipping_order_waives_the_base_fee_once(region, shipping):
    result = quote([DESK], region=region, coupon="FREESHIP")
    assert result.shipping == shipping
    assert result.total == 80000 + shipping


@pytest.mark.parametrize(
    ("unit_price", "coupon", "shipping"),
    [
        (49990, None, 3000),
        (50000, None, 0),
        (52000, "SAVE10", 3000),  # 47,000 after the discount
    ],
)
def test_free_shipping_depends_on_the_subtotal_after_the_discount(unit_price, coupon, shipping):
    result = quote([Item("lamp", unit_price, 1, 1.0)], coupon=coupon)
    assert result.shipping == shipping


@pytest.mark.parametrize(("items", "coupon"), [([BOOK], "FREESHIP"), ([DESK], None)])
def test_remote_surcharge_is_charged_when_the_base_fee_is_waived(items, coupon):
    assert quote(items, region="jeju", coupon=coupon).shipping == 3000


@pytest.mark.parametrize("coupon", ["save10", "Save10", " SAVE10 ", "\tsave10\n"])
def test_save10_code_ignores_case_and_surrounding_whitespace(coupon):
    result = quote([BOOK, MUGS], coupon=coupon)
    assert result.discount == 2000
    assert result.total == 21000


@pytest.mark.parametrize("coupon", ["freeship", " FreeShip "])
def test_freeship_code_ignores_case_and_surrounding_whitespace(coupon):
    assert quote([BOOK], coupon=coupon).shipping == 0


@pytest.mark.parametrize("coupon", ["HALFOFF", "SAVE 10", "", "   ", 10])
def test_unknown_coupon_is_rejected(coupon):
    with pytest.raises(ValueError, match="coupon"):
        quote([BOOK], coupon=coupon)


@pytest.mark.parametrize(
    "items",
    [
        [],
        [Item("book", 12000, 0, 0.4)],
        [Item("book", -1, 1, 0.4)],
        [Item("book", 12000, 1, 0)],
    ],
)
def test_invalid_orders_are_rejected(items):
    with pytest.raises(ValueError):
        quote(items)


def test_parcel_over_the_weight_limit_is_rejected():
    with pytest.raises(OverweightError):
        quote([Item("dumbbell", unit_price=30000, quantity=4, weight_kg=8.0)])
