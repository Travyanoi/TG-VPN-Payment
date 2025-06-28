from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from apps.shop.models import Discount


class DiscountEntity(BaseModel):
    pk: int
    name: str
    percent: int
    is_active: bool
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]

    @classmethod
    def from_model(cls, instance: 'Discount') -> 'DiscountEntity':
        return cls(
            pk=instance.pk,
            name=instance.name,
            percent=instance.percent,
            is_active=instance.is_active,
            starts_at=instance.starts_at,
            ends_at=instance.ends_at,
        )
