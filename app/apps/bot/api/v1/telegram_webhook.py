import structlog
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telebot.types import Update

from apps.bot.bot import bot as tg_bot

logger = structlog.get_logger("bot.api.telegram_webhook")


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

        except KeyError as parse_exc:
            logger.error("Invalid update format", exc_info=True, detail=str(parse_exc), data=request.data)
            return Response(
                {
                    "status": "error",
                    "message": "Invalid update payload"
                },
                # BAD DECISION
                status=status.HTTP_200_OK
            )

        except Exception as exc:
            logger.error("Unhandled exception during Telegram update processing", exc_info=True, data=request.data)
            return Response({"status": "error", "message": "Unhandled exception"}, status=status.HTTP_200_OK)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
