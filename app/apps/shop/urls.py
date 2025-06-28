from django.urls import re_path

from apps.shop.api.v1.payment_hook import PaymentHookView

urlpatterns = [
    re_path(r"payment_hook/(?P<class_name>[\w\-.]+)?", PaymentHookView.as_view(), name='payment_hook')
]
