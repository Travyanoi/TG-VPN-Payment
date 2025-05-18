from typing import Optional
from apps.bot.repositories.base import BaseRepository
from apps.shop.domain.discount import DiscountEntity
from apps.shop.models import Discount


class DiscountRepository(BaseRepository[DiscountEntity]):
    def get_by_id(self, pk: int) -> Optional['DiscountEntity']:
        try:
            instance = Discount.objects.get(pk=pk)
            return DiscountEntity.from_model(instance)
        except Discount.DoesNotExist:
            return None

    def create(self, **kwargs) -> DiscountEntity:
        instance = Discount.objects.create(**kwargs)
        return DiscountEntity.from_model(instance)

    def save(self, entity: 'DiscountEntity') -> 'DiscountEntity':
        instance, _ = Discount.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "name": entity.name,
                "percent": entity.percent,
                "is_active": entity.is_active,
                "starts_at": entity.starts_at,
                "ends_at": entity.ends_at,
            }
        )
        return DiscountEntity.from_model(instance)

    def delete(self, entity: 'DiscountEntity') -> None:
        Discount.objects.filter(pk=entity.pk).delete()
