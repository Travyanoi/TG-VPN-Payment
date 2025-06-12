from typing import Iterator
from unittest.mock import Mock, patch

import pytest
from rest_framework.response import Response

from apps.shop.factories import PurchaseFactory, PaySystemFactory
from apps.shop.models import Purchase, PaySystem


@pytest.fixture
def f_purchase() -> Iterator['Purchase']:
    yield PurchaseFactory()


@pytest.fixture
def f_pay_system() -> Iterator['PaySystem']:
    yield PaySystemFactory()


@pytest.fixture
def m_pay_system_payment_hook() -> Mock:
    with patch(
            "apps.shop.services.resolve_pay_system_handler."
            "ResolvePaySystemHandlerService.resolve_paysystem_handler"
    ) as m:
        m.payment_hook.return_value = Response(status=200)

        m.return_value = lambda a, b, pk: m

        yield m


@pytest.fixture
def m_resolve_paysystem_handler_attribute_error():
    with patch(
            "apps.shop.services.resolve_pay_system_handler."
            "ResolvePaySystemHandlerService.resolve_paysystem_handler"
    ) as m:
        m.side_effect = AttributeError("class not found")
        yield m
