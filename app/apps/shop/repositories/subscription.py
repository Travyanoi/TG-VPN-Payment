from typing import Optional

from apps.bot.repositories.base import BaseRepository
from apps.shop.domain.subscription import SubscriptionEntity
from apps.shop.models import Subscription


class SubscriptionRepository(BaseRepository[SubscriptionEntity]):
    def get_by_id(self, pk: int) -> Optional['SubscriptionEntity']:
        try:
            instance = Subscription.objects.get(pk=pk)
            return SubscriptionEntity.from_model(instance)
        except Subscription.DoesNotExist:
            return None

    def create(self, **kwargs) -> SubscriptionEntity:
        instance = Subscription.objects.create(**kwargs)
        return SubscriptionEntity.from_model(instance)

    def save(self, entity: 'SubscriptionEntity') -> 'SubscriptionEntity':
        instance, _ = Subscription.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "user_id": entity.user_id,
                "server_id": entity.server_id,
                "created_date": entity.created_date,
                "start_date": entity.start_date,
                "expired_date": entity.expired_date,
            }
        )
        return SubscriptionEntity.from_model(instance)

    def delete(self, entity: 'SubscriptionEntity') -> None:
        Subscription.objects.filter(pk=entity.pk).delete()
