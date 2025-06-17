from decimal import Decimal

import pytest

from apps.shop.domain.price_duration import PriceDurationEntity
from apps.shop.domain.usecases.calculate_price import PriceDurationInputDTO, CalculateProductPriceUseCase
from apps.shop.models import PriceDuration

pytestmark = [pytest.mark.django_db]


def test_price_duration_instance(f_price_duration: 'PriceDuration'):
    assert f_price_duration.product is not None
    assert f_price_duration.discount is not None
    assert isinstance(f_price_duration.duration, int)


def test_product_active_without_discount(f_price_duration: 'PriceDuration'):
    f_price_duration.discount = None
    f_price_duration.save(update_fields=["discount"])

    entity = PriceDurationEntity.from_model(f_price_duration)
    input_dto = PriceDurationInputDTO.from_entity(entity)
    use_case = CalculateProductPriceUseCase()

    result = use_case.execute(input_dto)

    months = Decimal(input_dto.duration) / Decimal(30)
    expected_total = (f_price_duration.product.base_price * months).quantize(Decimal("0.01"))

    assert result.base_price == f_price_duration.product.base_price


assert result.discount_percent is None
assert result.total_price == expected_total


def test_product_active_with_discount(f_price_duration, f_active_discount):
    f_price_duration.discount = f_active_discount
    f_price_duration.save()

    entity = PriceDurationEntity.from_model(f_price_duration)
    input_dto = PriceDurationInputDTO.from_entity(entity)
    use_case = CalculateProductPriceUseCase()
    result = use_case.execute(input_dto)

    months = Decimal(input_dto.duration) / Decimal(30)
    base_total = f_price_duration.product.base_price * months
    expected = (base_total * Decimal(100 - f_active_discount.percent) / Decimal(100)).quantize(Decimal('0.01'))

    assert result.discount_percent == f_active_discount.percent
    assert result.total_price == expected


def test_product_inactive_raises_value_error(f_price_duration):
    f_price_duration.product.is_active = False
    f_price_duration.product.save()

    entity = PriceDurationEntity.from_model(f_price_duration)
    input_dto = PriceDurationInputDTO.from_entity(entity)
    use_case = CalculateProductPriceUseCase()

    with pytest.raises(ValueError, match="Продукт недоступен"):
        use_case.execute(input_dto)


def test_discount_future_not_started(f_price_duration, f_future_discount):
    f_price_duration.discount = f_future_discount
    f_price_duration.save()

    entity = PriceDurationEntity.from_model(f_price_duration)
    input_dto = PriceDurationInputDTO.from_entity(entity)
    use_case = CalculateProductPriceUseCase()

    with pytest.raises(ValueError, match="Скидка неактивна"):
        use_case.execute(input_dto)


def test_discount_expired_raises(f_price_duration, f_expired_discount):
    f_price_duration.discount = f_expired_discount
    f_price_duration.save()

    entity = PriceDurationEntity.from_model(f_price_duration)
    input_dto = PriceDurationInputDTO.from_entity(entity)
    use_case = CalculateProductPriceUseCase()

    with pytest.raises(ValueError, match="Скидка неактивна"):
        use_case.execute(input_dto)
