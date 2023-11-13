from django.http import JsonResponse

from settings.settings import TELEGRAM_SECRET_TOKEN, WEBHOOK_PATH


class ValidateTelegramTokenMiddleware:
    SECRET_TOKEN = TELEGRAM_SECRET_TOKEN

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == WEBHOOK_PATH:
            header_token = request.META.get('HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN')
            if header_token is None or header_token != self.SECRET_TOKEN:
                #logger.warning(f"Попытка взлома, неправильный токен, ip={request.META.get('REMOTE_ADDR')}")
                print(f"Попытка взлома, неправильный токен, ip={request.META.get('REMOTE_ADDR')}")
                return JsonResponse({'error': 'Invalid Token'}, status=403)
        return self.get_response(request)