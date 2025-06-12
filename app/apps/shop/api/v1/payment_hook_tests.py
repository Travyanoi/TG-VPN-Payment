from unittest.mock import Mock
from urllib.parse import urljoin

import pytest
from rest_framework.test import APIClient

from apps.shop.models import PaySystem

pytestmark = [pytest.mark.django_db]


def test_valid_request_and_class_name(
        f_pay_system: 'PaySystem',
        f_api_client: 'APIClient',
        m_pay_system_payment_hook: Mock
):
    response = f_api_client.post(
        urljoin('/payment_hook/', f_pay_system.class_name),
        data={'amount': 150},
        format='json',
    )

    assert response.status_code == 200


def test_data_is_none(
        f_pay_system: 'PaySystem',
        f_api_client: 'APIClient',
        m_pay_system_payment_hook: Mock
):
    response = f_api_client.post(
        urljoin('/payment_hook/', f_pay_system.class_name),
        data=None
    )

    assert response.status_code == 400


def test_payment_system_not_found(
        f_api_client: 'APIClient',
        m_pay_system_payment_hook: 'Mock'
):
    fake_pay_system = "FakePaySystemTest"
    response = f_api_client.post(
        urljoin('/payment_hook/', fake_pay_system),
        data={'amount': 150},
        format='json',
    )

    assert response.status_code == 404
    assert f"PaySystem with class name [{fake_pay_system}] not found" in response.data["detail"]


def test_payment_hook_class_not_found(
        f_pay_system: 'PaySystem',
        f_api_client: 'APIClient',
        m_resolve_paysystem_handler_attribute_error: Mock
):
    response = f_api_client.post(
        urljoin('/payment_hook/', f_pay_system.class_name),
        data={'amount': 150},
        format='json',
    )

    assert response.status_code == 404
    assert f"Handler class for [{f_pay_system.class_name}] not found" in response.data["detail"]
    assert m_resolve_paysystem_handler_attribute_error.called
    assert m_resolve_paysystem_handler_attribute_error.call_count == 1
