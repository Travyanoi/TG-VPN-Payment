# repositories/shop_repository.py

from apps.shop.models import Product, PriceDuration, purchase, Subscription, Payment
from django.utils import timezone
from typing import Optional


class ProductRepository:
    def get_active(self):
        return Product.objects.filter(is_active=True)

    def get_by_id(self, product_id: int) -> Product:
        return Product.objects.get(id=product_id)


class PriceDurationRepository:
    def get_for_product(self, product_id: int):
        return PriceDuration.objects.filter(product_id=product_id)

    def get_by_id(self, price_id: int) -> PriceDuration:
        return PriceDuration.objects.get(id=price_id)


class PaymentRepository:
    def create(self, user, purchase: Purchase, pay_system, ip: Optional[str] = None) -> Payment:
        return Payment.objects.create(
            user=user,
            purchase=purchase,
            pay_system=pay_system,
            ip=ip
        )

    def set_status(self, payment: Payment, status: Payment.StatusCode, error_detail=None):
        payment.status_code = status
        if error_detail:
            payment.error_detail = error_detail
        payment.save()

    def get_by_internal_id(self, internal_id: str) -> Payment:
        return Payment.objects.get(internal_id=internal_id)

    def get_user_payments(self, user_id: str):
        return Payment.objects.filter(user_id=user_id).order_by("-create_date")
