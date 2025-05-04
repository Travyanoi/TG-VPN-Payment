from django.urls import path

from apps.bot.api.v1.telegram_webhook import TelegramWebhookView

urlpatterns = [
    path('webhook/', TelegramWebhookView.as_view()),
]
