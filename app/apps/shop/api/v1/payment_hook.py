from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from apps.shop.models import PaySystem


class PaymentHookView(APIView):
    def post(self, request, class_name):
        return self._request(request, class_name)

    def get(self, request, class_name):
        return self._request(request, class_name)

    def _request(self, request, class_name):
        data = request.data

        if not data:
            raise ValidationError("no data")

        # TODO Uebat' 404 response + logger if payment_system is None
        payment_system = PaySystem.objects.filter(class_name__iexact=class_name).first()

        cls = payment_system.get_class()
        cls_obj = cls(None, None, request, payment_system)

        return cls_obj.payment_hook(request)
