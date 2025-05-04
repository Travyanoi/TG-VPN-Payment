from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.shop.models import PriceDuration, Product


class PurchaseRepository:
    def create(self, user, price_duration: 'PriceDuration', product: 'Product') -> Purchase:
        return Purchase.objects.create(
            user=user,
            price_duration=price_duration,
            product=product,
            amount=price_duration.amount,
            currency=price_duration.currency
        )

    def get_by_token(self, token: str) -> Purchase:
        return Purchase.objects.get(token=token)

    def get_user_purchases(self, user_id: str):
        return Purchase.objects.filter(user_id=user_id).order_by("-created_date")
