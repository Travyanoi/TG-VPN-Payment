from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.shop.models import Payment


class PaymentEntity(BaseModel):
    pk: int
    user_id: str
    purchase_id: int
    pay_system_id: int
    status_code: Optional[int]
    error_detail: Optional[dict]
    ip: Optional[str]
    internal_id: str
    create_date: datetime

    @classmethod
    def from_model(cls, instance: 'Payment') -> 'PaymentEntity':
        return cls(
            pk=instance.pk,
            user_id=instance.user_id,
            purchase_id=instance.purchase_id,
            pay_system_id=instance.pay_system_id,
            status_code=instance.status_code,
            error_detail=instance.error_detail,
            ip=instance.ip,
            internal_id=instance.internal_id,
            create_date=instance.create_date,
        )
