from celery import chain
from apps.bot.tasks import add_user_to_wireguard, notify_user_addition_status


def build_user_addition_pipeline(server_id: int, chat_id: str, queue_send: str):
    return chain(
        add_user_to_wireguard.s(server_id, chat_id).set(queue=queue_send),
        notify_user_addition_status.s().set(queue="default")
    )
