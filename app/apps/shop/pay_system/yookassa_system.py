import logging

from django.http import JsonResponse
from rest_framework.exceptions import ValidationError, NotFound

from apps.core.redis_mutex import RedisMutex
from apps.shop.models import Payment
from settings.settings import SHOP_ID, SHOP_SECRET_KEY

from yookassa import Configuration, Payment as YooKassaPayment

Configuration.account_id = SHOP_ID
Configuration.secret_key = SHOP_SECRET_KEY


class YooKassaError(ValidationError):
    pass


class YooKassa:
    status_map = {
        'waiting': 1,
        'paid': 2,
        'error': 6
    }

    def __init__(self, purchase, user, request, pay_system):
        self.pay_system = pay_system
        self.purchase = purchase
        self.pay_id = purchase and self.purchase.pk
        self.description = purchase and purchase.buy_desc
        self.user = user
        self.request = request
        self.return_url = "https://t.me/vpntest1231bot"

    def serialize(self, purchase):
        payload = {
            "pay_id": self.pay_id,
            "amount": purchase.amount,
            "currency": purchase.currency,
            "description": self.description,
        }
        logging.info(payload)
        return payload

    def create_payment(self):
        yokassa_payment = YooKassaPayment.create({
            "amount": {
                "value": f"{self.purchase.amount}",
                "currency": f"{self.purchase.currency}"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{self.return_url}"
            },
            "capture": True,
            "description": f"{self.purchase.buy_desc}"
        }, self.purchase.token)

        try:
            payment = Payment(
                user=self.user,
                pay_system=self.pay_system,
                status_code=self.status_map.get("waiting"),
                ip=self.request.META.get("HTTP_CF_CONNECTING_IP") or self.request.META.get(
                    'HTTP_X_REAL_IP') or self.request.META.get('REMOTE_ADDR'),
                purchase=self.purchase,
                internal_id=self.purchase.token
            )
            payment.save()
            self.user.log(
                f"create_payment {self.purchase.id} {self.purchase} {self.purchase.funds} {self.user.currency}"
            )

            return {
                'payment_url': yokassa_payment.confirmation.confirmation_url,
                'status': self.status_map.get("waiting")
            }
        except Exception:
            raise YooKassaError(yokassa_payment.confirmation.confirmation_url)

    def payment_hook(self, request):
        data = request.data
        data_object = data.get("object")
        if 'id' not in data_object:
            raise NotFound("Data object has not id field")

        with RedisMutex().acquire_lock(f"id_{data_object['id']}"):
            payment = Payment.objects.filter(internal_id=data_object['id']).first()
            if not payment:
                logging.error(data)
                raise NotFound("Payment не найден")

            return JsonResponse({'status': 'ok'})
