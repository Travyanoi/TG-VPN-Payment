from typing import Optional
from apps.bot.repositories.base import BaseRepository
from apps.shop.domain.price_duration import PriceDurationEntity
from apps.shop.models import PriceDuration


class PriceDurationRepository(BaseRepository[PriceDurationEntity]):
    def get_by_id(self, pk: int) -> Optional[PriceDurationEntity]:
        try:
            instance = PriceDuration.objects.get(pk=pk)
            return PriceDurationEntity.from_model(instance)
        except PriceDuration.DoesNotExist:
            return None

    # TODO добавить для всех
    def get_by_product_id(self, product_id: int) -> list[Optional['PriceDurationEntity']]:
        instances = PriceDuration.objects.filter(product_id=product_id)
        return [PriceDurationEntity.from_model(instance) for instance in instances]

    def create(self, **kwargs) -> PriceDurationEntity:
        instance = PriceDuration.objects.create(**kwargs)
        return PriceDurationEntity.from_model(instance)

    def save(self, entity: PriceDurationEntity) -> PriceDurationEntity:
        instance, _ = PriceDuration.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "product_id": entity.product_id,
                "duration": entity.duration,
                "currency": entity.currency,
                "discount_id": entity.discount_id,
            }
        )
        return PriceDurationEntity.from_model(instance)

    def delete(self, entity: PriceDurationEntity) -> None:
        PriceDuration.objects.filter(pk=entity.pk).delete()
