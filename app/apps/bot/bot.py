import telebot
import datetime
import re

from io import BytesIO

from wireguard_tools import WireguardKey

from apps.bot.keyboards import global_kb
from apps.bot.models import UserInfo, InfoForConfFile, ServerConfInfo
from apps.bot.templates import *
from settings.settings import WG_CONF_ROOT, BOT_SECRET_TOKEN, WEBHOOK_PATH, TELEGRAM_SECRET_TOKEN

regex_for_digit = re.compile(r"(\d+)")
bot = telebot.TeleBot(BOT_SECRET_TOKEN)


def send_conf_file(chat_id: UserInfo.chat_id, message_id: int):
    byte_string = conf_file_for_user(chat_id)

    byte_string.seek(0)

    bot.delete_message(chat_id=chat_id, message_id=message_id)
    bot.send_document(chat_id=chat_id, document=byte_string, visible_file_name="WireGuard.conf")

# def check_sub():
#     kb = [global_kb[1]]
#
#     for client_subscription in InfoForConfFile.objects.filter(enable=True)
#
#         expiration_date = client_subscription.expires_at
#         now_date = datetime.datetime.now(tz=datetime.UTC)
#         delta_time = expiration_date - now_date
#
#         if delta_time.days == 0:
#             bot.send_message(
#                 chat_id=client_subscription.client_id,
#                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
#                 text=soon_sub_expired_text
#             )
#
#         elif delta_time.days < 0:
#             client_subscription.enable = False
#             client_subscription.save()
#
#             bot.send_message(
#                 chat_id=client_subscription.client_id,
#                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
#                 text=sub_expired_text
#             )
#
#     conf_file_formatter()
#
#
def resub(chat_id: UserInfo.chat_id, resub_time_in_months: str):

    client: InfoForConfFile = InfoForConfFile.objects.get(chat_id=chat_id)

    expiration_date = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=30 * int(resub_time_in_months))
    client.expires_at = expiration_date
    client.enable = True
    client.save()


def conf_file_for_user(chat_id: UserInfo.chat_id) -> BytesIO:

    db_conf_info: InfoForConfFile = InfoForConfFile.objects.get(chat_id_id=chat_id)
    db_server_info: ServerConfInfo = ServerConfInfo.objects.first()

    file = BytesIO()
    file.write(
        "[Interface]\n"
        f"Privatekey = {db_conf_info.privatekey}\n"
        f"Address = {db_conf_info.address}\n"
        "DNS = 8.8.8.8\n\n"
        "[Peer]\n"
        f"PublicKey = {db_server_info.publickey}\n"
        "AllowedIPs = 0.0.0.0/0\n"
        f"Endpoint = {db_server_info.end_point}\n"
        "PersistentKeepalive = 20".encode('utf-8')
    )

    return file


def conf_file_formatter():

    with open(f"{WG_CONF_ROOT}\wg0.conf", 'w') as output_file:
        server_data = ServerConfInfo.objects.first()

        output_file.write(f"[Interface]\n"
                          f"PrivateKey = {server_data.privatekey}\n"
                          f"Address = 10.10.0.1/24\n"
                          f"ListenPort = 51830\n"
                          f"PostUp = /etc/wireguard/postup.sh\n"
                          f"PostDown = /etc/wireguard/postdown.sh\n\n")

        for client_info in InfoForConfFile.objects.filter(enable=True):

            output_file.write(f"#{client_info.first_name.encode('utf-8').decode()}\n"
                              f"[Peer]\n"
                              f"Publickey = {client_info.publickey}\n"
                              f"AllowedIPs = {client_info.address}\n\n")


def conf_db_formatter(chat_id: UserInfo.chat_id, duration_of_sub: str):

    username: UserInfo = UserInfo.objects.get(chat_id=chat_id)
    private_key = WireguardKey.generate()
    public_key = private_key.public_key()

    start_at_time = datetime.datetime.now(tz=datetime.UTC)

    expiration_date = start_at_time + datetime.timedelta(days=30 * int(duration_of_sub))

    last_octet = InfoForConfFile.objects.count() + 2
    address_for_user = f"10.0.0.{last_octet}/32"

    InfoForConfFile.objects.get_or_create(
        chat_id_id=username.chat_id,
        defaults={
            "first_name": username.first_name,
            "address": address_for_user,
            "publickey": public_key,
            "privatekey": private_key,
            "start_at": start_at_time,
            "expires_at": expiration_date,
            "enable": True,
        }
    )


@bot.message_handler(commands=['start'])
def cmd_start(message: telebot.types.Message):
    kb= [global_kb[0]] + [global_kb[1]] + [global_kb[2]]
    UserInfo.objects.get_or_create(
        chat_id=message.chat.id,
        defaults={
            "first_name": message.chat.first_name or "",
            "last_name": message.chat.last_name or "",
            "username": message.chat.username or ""
        }
    )

    bot.send_message(
        chat_id=message.chat.id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text=greetings_text
    )


@bot.callback_query_handler(func=lambda call: call.data == 'buy_sub')
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = [global_kb[3]] + [global_kb[4]] + [global_kb[5]] + [global_kb[6]]
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text="Пожалуйста, выберите продолжительность подписки!"
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_month_sub'))
def payment_cmd(message: telebot.types.CallbackQuery):
    kb= [global_kb[1]] + [global_kb[2]]

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        text="Сейчас все сделаю..."
    )

    duration_of_subscription = re.split(regex_for_digit, message.data)

    conf_db_formatter(message.message.chat.id, str(duration_of_subscription[1]))
    conf_file_formatter()
    send_conf_file(message.message.chat.id, message.message.message_id)

    bot.send_message(
        chat_id=message.message.chat.id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text=conf_file_text
    )


@bot.callback_query_handler(func=lambda call: call.data == "rebuild_conf_file")
def rebuild_conf_cmd(message: telebot.types.CallbackQuery):

    kb= [global_kb[0]] + [global_kb[2]]

    client = InfoForConfFile.objects.get(chat_id=message.message.chat.id)

    if client.enable is True:
        send_conf_file(message.message.chat.id, message.message.message_id)

        bot.send_message(
            chat_id=message.message.chat.id,
            reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
            text=conf_file_text
        )
    else:
        bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
            text=sub_expired_text
        )


@bot.callback_query_handler(func=lambda call: call.data == "duration")
def duration_sub_cmd(message: telebot.types.CallbackQuery):
    kb = [global_kb[1]] + [global_kb[11]] + [global_kb[2]]

    client = InfoForConfFile.objects.get(chat_id=message.message.chat.id)

    expiration_date = client.expires_at

    now_date = datetime.datetime.now(tz=datetime.UTC)
    delta_time = expiration_date - now_date
    if int(delta_time.days) > 0:
        bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
            text=f"До конца вашей подписки осталось {int(delta_time.days)} дней"
        )
    else:
        bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
            text=sub_expired_text
        )


@bot.callback_query_handler(func=lambda call: call.data == "resub")
def resub_cmd(message: telebot.types.CallbackQuery):
    kb = [global_kb[7]] + [global_kb[8]] + [global_kb[9]] + [global_kb[10]]
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text=choose_duration_of_sub_text
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith("_month_resub"))
def resub_payment(message: telebot.types.CallbackQuery):
    kb = [global_kb[1]] + [global_kb[11]] + [global_kb[2]]

    duration_of_subscription = re.split(regex_for_digit, message.data)

    resub(message.message.chat.id, duration_of_subscription[1])
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text=successful_resub_text
    )


def BotPolling():
    # Удаление предыдущего вебхука, если он был настроен
    bot.remove_webhook()
    # Установка нового вебхука
    bot.set_webhook(url=f"{WEBHOOK_PATH}/webhook/")