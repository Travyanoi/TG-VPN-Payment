from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from django.utils import timezone

from apps.core.domain.usecases.base import BaseUseCaseInputDTO, BaseUseCase, BaseUseCaseOutputDTO
from apps.shop.domain.price_duration import PriceDurationEntity
from apps.shop.repositories.discount import DiscountRepository
from apps.shop.repositories.product import ProductRepository


class PriceDurationInputDTO(BaseUseCaseInputDTO):
    product_id: int
    duration: int
    currency: str
    discount_id: Optional[int]

    @classmethod
    def from_entity(cls, entity: 'PriceDurationEntity'):
        return cls(
            product_id=entity.product_id,
            duration=entity.duration,
            currency=entity.currency,
            discount_id=entity.discount_id,
        )


class CalculateProductPriceOutputDTO(BaseUseCaseOutputDTO):
    base_price: Decimal
    discount_percent: Optional[int]
    total_price: Decimal


class CalculateProductPriceUseCase(BaseUseCase[PriceDurationInputDTO, CalculateProductPriceOutputDTO]):
    def __init__(self):
        super().__init__()
        self.product_repository = ProductRepository()
        self.discount_repository = DiscountRepository()

    def _execute(self, input_dto: PriceDurationInputDTO) -> CalculateProductPriceOutputDTO:
        product = self.product_repository.get_by_id(input_dto.product_id)

        if not product or not product.is_active:
            raise ValueError("Продукт недоступен для покупки либо его уже не существует")

        discount_percent = None
        if input_dto.discount_id is not None:
            discount = self.discount_repository.get_by_id(input_dto.discount_id)

            now = timezone.now()
            if not discount.is_active or \
                    (discount.starts_at and discount.starts_at > now) or \
                    (discount.ends_at and discount.ends_at < now):
                raise ValueError("Скидка неактивна или не действует сейчас")

            discount_percent = discount.percent

        months = Decimal(input_dto.duration) / Decimal(30)
        months = months.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        total_price = product.base_price * months

        if discount_percent:
            discount_multiplier = Decimal(100 - discount_percent) / Decimal(100)
            total_price *= discount_multiplier

        return CalculateProductPriceOutputDTO(
            base_price=product.base_price,
            discount_percent=discount_percent,
            total_price=total_price.quantize(Decimal('0.01'))
        )
