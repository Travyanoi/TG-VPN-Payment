from django.utils import timezone

from apps.shop.models import Subscription


class SubscriptionRepository:
    def get_user_active(self, user_id: str):
        return Subscription.objects.filter(
            user_id=user_id,
            expired_date__gt=timezone.now()
        )

    def create_or_update(self, user, product, start_date, expired_date) -> Subscription:
        obj, _ = Subscription.objects.update_or_create(
            user=user,
            product=product,
            defaults=dict(start_date=start_date, expired_date=expired_date)
        )
        return obj
