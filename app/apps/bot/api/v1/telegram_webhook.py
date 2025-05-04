from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from telebot.types import Update

from apps.bot.bot import bot as tg_bot


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):

    def post(self, request):
        return self._request(request)

    def get(self, request):
        return self._request(request)

    def _request(self, request, *args, **kwargs):
        try:
            update = Update.de_json(request.data)
            tg_bot.process_new_updates([update])
        except Exception as e:
            raise NotFound(f"Telegram Webhook error: {e}")

        return Response({"status": "ok"})
