from typing import TYPE_CHECKING
from decimal import Decimal
from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.shop.models import Product


class ProductEntity(BaseModel):
    pk: int
    name: str | None
    description: str | None
    base_price: Decimal
    is_active: bool

    @classmethod
    def from_model(cls, instance: 'Product') -> 'ProductEntity':
        return cls(
            pk=instance.pk,
            name=instance.name,
            description=instance.description,
            base_price=instance.base_price,
            is_active=instance.is_active,
        )
