import datetime
import re

import structlog
import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton

from apps.bot.domain.usecases.create_conf_file_for_user import CreateConfigFileForUserUseCase, InfoForConfFileInputDTO
from apps.bot.exception_handler import MyExceptionHandler
from apps.bot.keyboards import global_kb
from apps.bot.models import UserInfo, InfoForConfFile, ServerConfInfo
from apps.bot.repositories.info_for_conf_file import InfoForConfFileRepository
from apps.bot.repositories.server_conf_info import ServerConfInfoRepository
from apps.bot.templates import *
from apps.bot.workflows.user_addition_amnesiawg import build_user_addition_pipeline
from apps.shop.domain.usecases.create_purchase import CreatePurchaseUseCase, CreatePurchaseInputDTO
from apps.shop.models import PriceDuration, Purchase
from apps.shop.repositories.pay_system import PaySystemRepository
from apps.shop.repositories.price_duration import PriceDurationRepository
from apps.shop.repositories.product import ProductRepository
from apps.shop.services.resolve_pay_system_handler import ResolvePaySystemHandlerService
from settings.settings import WG_CONF_ROOT, BOT_SECRET_TOKEN, WEBHOOK_PATH, TELEGRAM_SECRET_TOKEN

regex_for_digit = re.compile(r"(\d+)")
bot = telebot.TeleBot(BOT_SECRET_TOKEN, exception_handler=MyExceptionHandler())

logger = structlog.getLogger("bot.bot")


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


def resub(chat_id: UserInfo.chat_id, resub_time_in_months: int):
    client: InfoForConfFile = InfoForConfFile.objects.get(chat_id=chat_id)
    resub_duration = datetime.timedelta(days=30 * int(resub_time_in_months))

    if client.enable:
        client.expires_at = client.expires_at + resub_duration
    else:
        current_time = datetime.datetime.now(tz=datetime.UTC)
        client.expires_at = current_time + resub_duration

    client.enable = True
    client.save()


def conf_file_formatter():
    with open(f"{WG_CONF_ROOT}\\wg0.conf", 'w') as output_file:
        server_data = ServerConfInfo.objects.first()

        output_file.write(f"[Interface]\n"
                          f"PrivateKey = {server_data.privatekey}\n"
                          f"Address = 10.10.0.1/24\n"
                          f"ListenPort = 51830\n"
                          f"PostUp = /etc/wireguard/postup.sh\n"
                          f"PostDown = /etc/wireguard/postdown.sh\n\n")

        for client_info in InfoForConfFile.objects.filter(enable=True):
            output_file.write(f"#{client_info.chat_id_id}\n"
                              f"[Peer]\n"
                              f"Publickey = {client_info.publickey}\n"
                              f"AllowedIPs = {client_info.address}\n\n")


# def conf_db_formatter(chat_id: UserInfo.chat_id, duration_of_sub: int):
#     username: UserInfo = UserInfo.objects.get(chat_id=chat_id)
#     private_key = WireguardKey.generate()
#     public_key = private_key.public_key()
#
#     start_at_time = datetime.datetime.now(tz=datetime.UTC)
#
#     expiration_date = start_at_time + datetime.timedelta(days=30 * int(duration_of_sub))
#
#     # TODO """
#     #  считать общее количество записей на конкретном сервере(server_id) и делить на 255
#     #  для определения подсетки
#
#     last_octet = InfoForConfFile.objects.count() + 2
#     address_for_user = f"10.0.0.{last_octet}/32"
#
#     instance, created = InfoForConfFile.objects.get_or_create(
#         chat_id_id=username.chat_id,
#         defaults={
#             "first_name": username.first_name,
#             "address": address_for_user,
#             "publickey": public_key,
#             "privatekey": private_key,
#             "start_at": start_at_time,
#             "expires_at": expiration_date,
#             "enable": True,
#         }
#     )
#
#   return instance, created


@bot.message_handler(commands=['start'])
def cmd_start(message: telebot.types.Message):
    kb = [global_kb[0]] + [global_kb[1]] + [global_kb[2]]

    # # TODO репозиторий
    # UserInfo.objects.get_or_create(
    #     chat_id=message.chat.id,
    #     defaults={
    #         "first_name": message.chat.first_name or "",
    #         "last_name": message.chat.last_name or "",
    #         "username": message.chat.username or ""
    #     }
    # )
    #
    # bot.send_message(
    #     chat_id=message.chat.id,
    #     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
    #     text=greetings_text
    # )

    dto = {
        "server_id": "1",
        "ssh_endpoint": "41.216.182.144",
    }

    build_user_addition_pipeline(dto=dto, queue_send="stockholm").apply_async()

def build_kb(data: list[tuple[str]]):
    return [
        [InlineKeyboardButton(text=kb_item[2], callback_data=f"{str(kb_item[0])}_id_purchase")]
        for kb_item in data
    ]


@bot.callback_query_handler(func=lambda call: call.data == 'buy_sub')
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    # data = PriceDuration.objects.values_list("id", "duration", "name")
    kb = []
    products = ProductRepository().all()
    for product in products:
        kb.append([InlineKeyboardButton(
            text=f"{product.name} - {product.base_price} Руб в месяц",
            callback_data=f"{str(product.pk)}_product"
        )])
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text="Выберите страну, в которой желаете получить VPN"
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith("_product"))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    product_id = message.data.split("_")[0]
    servers = ServerConfInfoRepository().get_by_product_id(int(product_id))
    for server in servers:
        kb.append([InlineKeyboardButton(text=server.name, callback_data=f"{product_id}_{str(server.pk)}_server")])
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text="Выберите сервер, на котором желаете получить VPN"
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith("_server"))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    split_data = message.data.split("_")
    product_id = split_data[0]
    server_id = split_data[1]

    price_durations = PriceDurationRepository().get_by_product_id(product_id=int(product_id))
    for duration in price_durations:
        kb.append([
            InlineKeyboardButton(
                text=f"{duration.duration} дней",
                callback_data=f"{duration.pk}_{product_id}_{server_id}_duration")
        ])

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text="Выберите длительности подписки!"
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith("_duration"))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []

    #server_id = message.data.split("_")[-2]

    # conf_file_entity = InfoForConfFileRepository().get_by_user_server_id(
    #     chat_id=str(message.message.chat.id),
    #     server_id=int(server_id)
    # )
    # conf_file_dto = InfoForConfFileInputDTO.from_entity(conf_file_entity)
    #
    # byte_string = CreateConfigFileForUserUseCase().execute(conf_file_dto)
    #
    # bot.delete_message(chat_id=message.message.chat.id, message_id=message.message.message_id)
    # try:
    #     bot.send_document(
    #         chat_id=message.message.chat.id,
    #         document=byte_string,
    #         visible_file_name=f"{message.message.chat.id}.conf"
    #     )
    # except ApiTelegramException as tele_exc:
    #     logger.error("Telegram API exception", exc_info=True, detail=str(tele_exc))
    #     bot.send_message(
    #         chat_id=message.message.chat.id,
    #         text="Произошла ошибка, обратитесь в поддержку!"
    #     )
    #
    # bot.send_message(
    #     chat_id=message.message.chat.id,
    #     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
    #     text=conf_file_text
    # )

    pay_systems = PaySystemRepository().all()
    for pay_system in pay_systems:
        callback = f"{pay_system.pk}_{"_".join(message.data.split("_")[:-1])}_paysystem"
        kb.append([
            InlineKeyboardButton(
                text=pay_system.name,
                callback_data=callback)
        ])

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text="Выберите способ оплаты!"
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith("_paysystem"))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    pay_system_id, duration_id, product_id, server_id, _ = message.data.split("_")
    purchase_input_dto = CreatePurchaseInputDTO(
        user_id=str(message.message.chat.id),
        price_duration_id=duration_id,
        product_id=product_id
    )
    purchase_output_dto = CreatePurchaseUseCase().execute(purchase_input_dto)
    paysystem_entity = PaySystemRepository().get_by_id(pay_system_id)
    payment_class = ResolvePaySystemHandlerService.resolve_paysystem_handler(paysystem_entity.class_name)
    payment_class_obj = payment_class(purchase_output_dto.purchase_id, message.message.chat.id, pay_system_id)
    payment_dict = payment_class_obj.create_payment()

    kb.append([InlineKeyboardButton(text="Ссылка на оплату", url=payment_dict.get("payment_url"))])

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text="Ссылка на оплату ниже, после оплаты вам придет файл"
    )

@bot.callback_query_handler(func=lambda call: call.data.endswith('_id_purchase'))
def payment_cmd(message: telebot.types.CallbackQuery):
    kb = [global_kb[1]] + [global_kb[2]]
    price_duration_object = PriceDuration.objects.get(id=message.data.split("_")[0])
    purchase = Purchase.objects.create(
        user_id=message.message.chat.id,
        price_duration_id=price_duration_object.id,
        amount=price_duration_object.amount,
        product_id=price_duration_object.product.id,
    )

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        text="Сейчас все сделаю..."
    )

    duration_of_subscription = re.split(regex_for_digit, message.data)

    instance, created = conf_db_formatter(message.message.chat.id, int(duration_of_subscription[1]))

    if not created:
        resub(message.message.chat.id, int(duration_of_subscription[1]))

    # conf_file_formatter()
    # send_conf_file(message.message.chat.id, message.message.message_id)
    #
    # bot.send_message(
    #     chat_id=message.message.chat.id,
    #     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
    #     text=conf_file_text
    # )


# TODO тут скорее всего должна быть прослойка с выбором конкретного сервера из возможных, если их несколько
@bot.callback_query_handler(func=lambda call: call.data == "rebuild_conf_file")
def rebuild_conf_cmd(message: telebot.types.CallbackQuery):
    kb = [global_kb[0]] + [global_kb[2]]

    client = InfoForConfFile.objects.get(chat_id=message.message.chat.id)

    if client.enable is True:
        # TODO Обращение к юзкейсу
        byte_string = conf_file_for_user(chat_id)

        byte_string.seek(0)

        bot.delete_message(chat_id=message.message.chat.id, message_id=message.message.message_id)
        bot.send_document(chat_id=message.message.chat.id, document=byte_string, visible_file_name="")

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

    resub(message.message.chat.id, int(duration_of_subscription[1]))
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text=successful_resub_text
    )


def bot_polling():
    # Удаление предыдущего вебхука, если он был настроен
    bot.remove_webhook()
    # Установка нового вебхука
    bot.set_webhook(
        url=f"{WEBHOOK_PATH}/webhook/",
        secret_token=TELEGRAM_SECRET_TOKEN,
    )
    logger.info(f"Webhook = {WEBHOOK_PATH}/webhook/")
