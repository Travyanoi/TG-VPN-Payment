from unittest.mock import patch

import pytest
from telebot import TeleBot
from telebot.types import Update


@pytest.fixture
def m_update_de_json():
    with patch.object(Update, "de_json") as m:
        yield m


@pytest.fixture
def m_process_new_updates():
    with patch.object(TeleBot, "process_new_updates") as m:
        yield m


@pytest.fixture
def m_process_new_updates_key_error():
    with patch.object(TeleBot, "process_new_updates", side_effect=KeyError) as m:
        yield m


@pytest.fixture
def m_process_new_updates_exception():
    with patch.object(TeleBot, "process_new_updates", side_effect=Exception) as m:
        yield m
