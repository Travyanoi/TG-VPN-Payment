from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.shop.models import Subscription


class SubscriptionEntity(BaseModel):
    pk: int
    user_id: str
    product_tariff_id: int
    created_date: datetime
    start_date: datetime
    expired_date: datetime

    @classmethod
    def from_model(cls, instance: 'Subscription') -> 'SubscriptionEntity':
        return cls(
            pk=instance.pk,
            user_id=instance.user.chat_id,
            product_tariff_id=instance.product_tariff.pk,
            created_date=instance.created_date,
            start_date=instance.start_date,
            expired_date=instance.expired_date,
        )
