from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.shop.models import PriceDuration


class PriceDurationEntity(BaseModel):
    pk: int
    product_id: int
    duration: int
    currency: str
    discount_id: Optional[int]

    @classmethod
    def from_model(cls, instance: 'PriceDuration') -> 'PriceDurationEntity':
        return cls(
            pk=instance.pk,
            product_id=instance.product.pk,
            duration=instance.duration,
            currency=instance.currency,
            discount_id=instance.discount.pk if instance.discount else None,
        )
