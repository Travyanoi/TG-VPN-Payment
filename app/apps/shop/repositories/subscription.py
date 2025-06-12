from abc import ABC
from typing import Optional

from django.utils import timezone

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
                "product_id": entity.product_id,
                "purchase_id": entity.purchase_id,
                "expires_at": entity.expires_at,
                "is_active": entity.is_active,
                "updated_at": entity.updated_at,
            }
        )
        return SubscriptionEntity.from_model(instance)

    def delete(self, entity: 'SubscriptionEntity') -> None:
        Subscription.objects.filter(pk=entity.pk).delete()
