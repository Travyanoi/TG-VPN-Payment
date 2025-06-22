import logging
from uuid import UUID

from django.http import JsonResponse
from rest_framework.exceptions import ValidationError, NotFound

from apps.bot.domain.usecases.create_conf_file import GetOrCreateConfFileUseCase, GetOrCreateConfFileInputDTO
from apps.bot.repositories.server_conf_info import ServerConfInfoRepository
from apps.bot.repositories.user_info import UserInfoRepository
from apps.bot.workflows.user_addition_amnesiawg import build_user_addition_pipeline
from apps.core.redis_mutex import RedisMutex
from apps.shop.domain.usecases.create_payment import CreatePaymentInputDTO, CreatePaymentUseCase
from apps.shop.domain.usecases.create_subscription import CreateSubscriptionUseCase, CreateSubscriptionInputDTO
from apps.shop.models import Payment
from apps.shop.repositories.payment import PaymentRepository
from apps.shop.repositories.price_duration import PriceDurationRepository
from apps.shop.repositories.purchase import PurchaseRepository
from apps.shop.repositories.subscription import SubscriptionRepository
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

    def __init__(self, purchase_id, chat_id, pay_system_id):
        self.pay_system_id = pay_system_id
        self.purchase_entity = PurchaseRepository().get_by_id(purchase_id)
        self.pay_id = purchase_id
        self.user_entity = UserInfoRepository().get_by_chat_id(chat_id)
        self.log = UserInfoRepository().log
        self.return_url = "https://t.me/vpntest1231bot"

    def serialize(self, purchase):
        payload = {
            "pay_id": self.pay_id,
            "amount": purchase.amount,
            "currency": purchase.currency,
            # "description": self.description,
        }
        logging.info(payload)
        return payload

    def create_payment(self):
        yokassa_payment = YooKassaPayment.create({
            "amount": {
                "value": f"{self.purchase_entity.amount}",
                "currency": f"{self.purchase_entity.currency}"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{self.return_url}"
            },
            "capture": True,
            "description": f"{self.purchase_entity.buy_descr}",
            "metadata": {
                "id": self.purchase_entity.token
            }
        })

        try:
            payment_input_dto = CreatePaymentInputDTO(
                purchase_id=self.purchase_entity.pk,
                pay_system_id=self.pay_system_id,
            )
            payment_output_dto = CreatePaymentUseCase().execute(payment_input_dto)

            self.log(
                chat_id=self.user_entity.chat_id,
                text=f"create payment: id = {payment_output_dto.payment_id} "
                     f"purchase id = {self.purchase_entity.pk}, currency = {self.purchase_entity.currency}"
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
        object_metadata = data_object.get("metadata")
        if 'id' not in object_metadata:
            raise NotFound("Metadata of data object has not id field")

        internal_id = object_metadata["id"]

        with (RedisMutex().acquire_lock(f"id_{internal_id}")):
            payment_repo = PaymentRepository()
            payment = payment_repo.get_by_internal_id(internal_id=internal_id)
            if not payment:
                logging.error(data_object)
                raise NotFound("Payment не найден")

            if data_object['status'] == "succeeded":
                payment.status_code = 2
                payment_repo.save(payment)

                purchase = PurchaseRepository().get_by_id(payment.purchase_id)
                server = ServerConfInfoRepository().get_by_id(purchase.server_id)
                price_duration_repo = PriceDurationRepository()
                price_duration = price_duration_repo.get_by_id(purchase.price_duration_id)

                sub_input_dto = CreateSubscriptionInputDTO(
                    user_id=payment.user_id,
                    server_id=server.pk,
                    duration_days=price_duration.duration
                )

                CreateSubscriptionUseCase().execute(sub_input_dto)

                conf_file_input_dto = GetOrCreateConfFileInputDTO(
                    user_id=payment.user_id,
                    server_id=server.pk,
                )

                GetOrCreateConfFileUseCase().execute(conf_file_input_dto)


                build_user_addition_pipeline(
                    server_id=server.pk,
                    chat_id=payment.user_id,
                    queue_send=server.queue_name,
                ).apply_async()

            return JsonResponse({'status': 'ok'})
