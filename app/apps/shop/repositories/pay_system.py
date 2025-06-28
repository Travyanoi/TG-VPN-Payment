from typing import Optional
from apps.bot.repositories.base import BaseRepository
from apps.shop.domain.pay_system import PaySystemEntity
from apps.shop.models import PaySystem


class PaySystemRepository(BaseRepository[PaySystemEntity]):
    def get_by_id(self, pk: int) -> Optional[PaySystemEntity]:
        try:
            instance = PaySystem.objects.get(pk=pk)
            return PaySystemEntity.from_model(instance)
        except PaySystem.DoesNotExist:
            return None

    def get_by_class_name(self, class_name: str) -> Optional[PaySystemEntity]:
        instance = PaySystem.objects.filter(class_name=class_name).first()
        return PaySystemEntity.from_model(instance) if instance else None

    def all(self) -> list[Optional[PaySystemEntity]]:
        instances = PaySystem.objects.all()
        return [PaySystemEntity.from_model(instance) for instance in instances]

    def create(self, **kwargs) -> PaySystemEntity:
        instance = PaySystem.objects.create(**kwargs)
        return PaySystemEntity.from_model(instance)

    def save(self, entity: PaySystemEntity) -> PaySystemEntity:
        instance, _ = PaySystem.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "name": entity.name,
                "description": entity.description,
                "is_active": entity.is_active,
                "is_test": entity.is_test,
                "class_name": entity.class_name,
                "ordering": entity.ordering,
            }
        )
        return PaySystemEntity.from_model(instance)

    def delete(self, entity: PaySystemEntity) -> None:
        PaySystem.objects.filter(pk=entity.pk).delete()
