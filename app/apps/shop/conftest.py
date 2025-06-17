from datetime import timedelta
from typing import Iterator
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone
from rest_framework.response import Response

from apps.shop.factories import PurchaseFactory, PaySystemFactory, PriceDurationFactory, DiscountFactory
from apps.shop.models import Purchase, PaySystem, PriceDuration, Discount


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


@pytest.fixture
def f_price_duration() -> Iterator['PriceDuration']:
    yield PriceDurationFactory()


@pytest.fixture
def f_expired_discount() -> Iterator['Discount']:
    now = timezone.now()
    discount = DiscountFactory(
        is_active=True,
        starts_at=now - timedelta(days=10),
        ends_at=now - timedelta(days=1),
    )
    yield discount


@pytest.fixture
def f_active_discount() -> Iterator['Discount']:
    now = timezone.now()
    discount = DiscountFactory(
        is_active=True,
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=10),
    )
    yield discount


@pytest.fixture
def f_future_discount() -> Iterator['Discount']:
    now = timezone.now()
    discount = DiscountFactory(
        is_active=True,
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=10),
    )
    yield discount
