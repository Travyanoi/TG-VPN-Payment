import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .bot import *


@csrf_exempt
async def webhook(request):
    up = json.loads(request.body)
    update_id = up.get('update_id')
    message = up.get('message')
    callback_query = up.get('callback_query')

    my_update = types.update.Update(
        update_id=update_id,
        message=message if message is not None else None,
        callback_query=callback_query if callback_query is not None else None
    )
    await dp.feed_update(bot=bot, update=my_update)
    return JsonResponse({'status': 'ok'})
