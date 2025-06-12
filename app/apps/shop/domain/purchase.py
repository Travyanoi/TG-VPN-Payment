from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.shop.models import Purchase


class PurchaseEntity(BaseModel):
    pk: int
    user_id: str
    price_duration_id: int
    product_id: int
    currency: str
    amount: Decimal
    created_date: datetime
    buy_descr: str
    token: str

    @classmethod
    def from_model(cls, instance: 'Purchase') -> 'PurchaseEntity':
        return cls(
            pk=instance.pk,
            user_id=instance.user_id,
            price_duration_id=instance.price_duration_id,
            product_id=instance.product_id,
            currency=instance.currency,
            amount=instance.amount,
            created_date=instance.created_date,
            buy_descr=instance.buy_descr,
            token=instance.token,
        )
