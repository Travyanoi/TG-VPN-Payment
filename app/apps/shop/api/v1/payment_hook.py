from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView

from apps.shop.repositories.pay_system import PaySystemRepository
from apps.shop.services.resolve_pay_system_handler import ResolvePaySystemHandlerService


class PaymentHookView(APIView):
    def post(self, request, class_name):
        return self._request(request, class_name)

    def get(self, request, class_name):
        return self._request(request, class_name)

    def _request(self, request, class_name):
        data = request.data

        if not data:
            raise ValidationError("Request doesn't contains a data")

        payment_system = PaySystemRepository().get_by_class_name(class_name=class_name)

        if not payment_system:
            raise NotFound(f"PaySystem with class name [{class_name}] not found")

        try:
            cls = ResolvePaySystemHandlerService.resolve_paysystem_handler(class_name)
        except AttributeError:
            raise NotFound(f"Handler class for [{class_name}] not found")

        cls_obj = cls(None, None, payment_system.pk)

        return cls_obj.payment_hook(request)
