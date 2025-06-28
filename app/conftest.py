import pytest
from rest_framework.test import APIClient


@pytest.fixture
def f_api_client() -> 'APIClient':
    client = APIClient()
    client.force_authenticate()
    yield client
