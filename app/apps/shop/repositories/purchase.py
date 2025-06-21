from typing import Optional, List

from apps.bot.repositories.base import BaseRepository
from apps.shop.domain.purchase import PurchaseEntity
from apps.shop.models import Purchase


class PurchaseRepository(BaseRepository[PurchaseEntity]):
    def get_by_id(self, pk: int) -> Optional[PurchaseEntity]:
        try:
            instance = Purchase.objects.get(pk=pk)
            return PurchaseEntity.from_model(instance)
        except Purchase.DoesNotExist:
            return None

    def get_by_user(self, user_id: str) -> List[PurchaseEntity]:
        instances = Purchase.objects.filter(user_id=user_id)
        return [PurchaseEntity.from_model(instance) for instance in instances]

    def create(self, **kwargs) -> PurchaseEntity:
        instance = Purchase.objects.create(**kwargs)
        return PurchaseEntity.from_model(instance)

    def save(self, entity: PurchaseEntity) -> PurchaseEntity:
        instance, _ = Purchase.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "user": entity.user,
                "price_duration_id": entity.price_duration_id,
                "server_id": entity.server_id,
                "currency": entity.currency,
                "amount": entity.amount,
                "created_date": entity.created_date,
                "token": entity.token,
            }
        )
        return PurchaseEntity.from_model(instance)

    def delete(self, entity: PurchaseEntity) -> None:
        Purchase.objects.filter(pk=entity.pk).delete()
