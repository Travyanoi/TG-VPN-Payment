from typing import Optional, List

from apps.bot.repositories.base import BaseRepository
from apps.shop.domain.payment import PaymentEntity
from apps.shop.models import Payment


class PaymentRepository(BaseRepository[PaymentEntity]):
    def get_by_id(self, pk: int) -> Optional[PaymentEntity]:
        try:
            instance = Payment.objects.get(pk=pk)
            return PaymentEntity.from_model(instance)
        except Payment.DoesNotExist:
            return None

    def get_by_purchase(self, purchase_id: int) -> List[PaymentEntity]:
        instances = Payment.objects.filter(purchase_id=purchase_id)
        return [PaymentEntity.from_model(instance) for instance in instances]

    def create(self, **kwargs) -> PaymentEntity:
        instance = Payment.objects.create(**kwargs)
        return PaymentEntity.from_model(instance)

    def save(self, entity: PaymentEntity) -> PaymentEntity:
        instance, _ = Payment.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "user_id": entity.user_id,
                "purchase_id": entity.purchase_id,
                "pay_system_id": entity.pay_system_id,
                "status_code": entity.status_code,
                "error_detail": entity.error_detail,
                "ip": entity.ip,
                "internal_id": entity.internal_id,
            }
        )
        return PaymentEntity.from_model(instance)

    def delete(self, entity: PaymentEntity) -> None:
        Payment.objects.filter(pk=entity.pk).delete()
