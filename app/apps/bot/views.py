import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .bot import *


@csrf_exempt
def webhook(request):
    json_str = request.body.decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    try:
        bot.process_new_updates([update])
    except Exception as e:
        print(e)

    return JsonResponse({'status':'ok'})
