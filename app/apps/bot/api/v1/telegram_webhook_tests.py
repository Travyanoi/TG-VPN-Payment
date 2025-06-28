from unittest.mock import Mock

import pytest
from rest_framework.test import APIClient

pytestmark = [pytest.mark.django_db]


def test_valid_telegram_webhook(
        f_api_client: 'APIClient',
        m_update_de_json: 'Mock',
        m_process_new_updates: 'Mock'
):
    response = f_api_client.post("/webhook/", data={}, format="json")

    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert m_update_de_json.called
    assert m_process_new_updates.called


def test_key_error_telegram_webhook(
        f_api_client: 'APIClient',
        m_update_de_json: 'Mock',
        m_process_new_updates_key_error: 'Mock'
):
    response = f_api_client.post("/webhook/", data={}, format="json")

    assert response.status_code == 200
    assert response.data["status"] == "error"
    assert response.data["message"] == "Invalid update payload"
    assert m_update_de_json.called
    assert m_process_new_updates_key_error.called


def test_exception_telegram_webhook(
        f_api_client: 'APIClient',
        m_update_de_json: 'Mock',
        m_process_new_updates_exception: 'Mock'
):
    response = f_api_client.post("/webhook/", data={}, format="json")

    assert response.status_code == 200
    assert response.data["status"] == "error"
    assert response.data["message"] == "Unhandled exception"
    assert m_update_de_json.called
    assert m_process_new_updates_exception.called
