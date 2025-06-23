import datetime
import re
from io import BytesIO

import structlog
import telebot
from telebot.types import InlineKeyboardButton

from apps.bot.exception_handler import MyExceptionHandler
from apps.bot.keyboards import global_kb
from apps.bot.models import UserInfo, InfoForConfFile, ServerConfInfo
from apps.bot.repositories.server_conf_info import ServerConfInfoRepository
from apps.bot.templates import *
from apps.shop.domain.usecases.create_purchase import CreatePurchaseUseCase, CreatePurchaseInputDTO
from apps.shop.repositories.pay_system import PaySystemRepository
from apps.shop.repositories.price_duration import PriceDurationRepository
from apps.shop.repositories.product import ProductRepository
from apps.shop.services.resolve_pay_system_handler import ResolvePaySystemHandlerService
from settings.settings import WG_CONF_ROOT, BOT_SECRET_TOKEN, WEBHOOK_PATH, TELEGRAM_SECRET_TOKEN

regex_for_digit = re.compile(r"(\d+)")
bot = telebot.TeleBot(BOT_SECRET_TOKEN, exception_handler=MyExceptionHandler())

logger = structlog.getLogger("bot.bot")


def send_conf_file(chat_id: int, file_data: bytes, file_name: str):
    file = BytesIO(file_data)

    bot.send_document(
        chat_id=chat_id,
        document=file,
        visible_file_name=f'{file_name}.conf',
    )


@bot.message_handler(commands=['start'])
def cmd_start(message: telebot.types.Message):
    kb = [global_kb[0]]

    # TODO репозиторий
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


def build_kb(data: list[tuple[str]]):
    return [
        [InlineKeyboardButton(text=kb_item[2], callback_data=f"{str(kb_item[0])}_id_purchase")]
        for kb_item in data
    ]


@bot.callback_query_handler(func=lambda call: call.data == 'buy_sub')
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    products = ProductRepository().all()
    for product in products:
        kb.append([InlineKeyboardButton(
            text=f'{product.name} - {product.base_price} Руб в месяц',
            callback_data=f'{str(product.pk)}_product'
        )
        ])
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text='Выберите страну, в которой желаете получить VPN'
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_product'))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    product_id = message.data.split("_")[0]
    servers = ServerConfInfoRepository().get_by_product_id(int(product_id))
    for server in servers:
        kb.append([InlineKeyboardButton(text=server.name, callback_data=f'{product_id}_{str(server.pk)}_server')])
    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text='Выберите сервер, на котором желаете получить VPN'
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_server'))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    split_data = message.data.split("_")
    product_id = split_data[0]
    server_id = split_data[1]

    price_durations = PriceDurationRepository().get_by_product_id(product_id=int(product_id))
    for duration in price_durations:
        kb.append([
            InlineKeyboardButton(
                text=f'{duration.duration} дней',
                callback_data=f'{duration.pk}_{product_id}_{server_id}_duration'
            )
        ])

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text='Выберите длительности подписки!'
    )


@bot.callback_query_handler(func=lambda call: call.data.endswith('_duration'))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []

    pay_systems = PaySystemRepository().all()
    for pay_system in pay_systems:
        callback = f'{pay_system.pk}_{"_".join(message.data.split("_")[:-1])}_paysystem'
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


@bot.callback_query_handler(func=lambda call: call.data.endswith('_paysystem'))
def buy_sub_cmd(message: telebot.types.CallbackQuery):
    kb = []
    pay_system_id, duration_id, product_id, server_id, _ = message.data.split("_")
    purchase_input_dto = CreatePurchaseInputDTO(
        user_id=str(message.message.chat.id),
        price_duration_id=duration_id,
        server_id=server_id
    )
    purchase_output_dto = CreatePurchaseUseCase().execute(purchase_input_dto)
    paysystem_entity = PaySystemRepository().get_by_id(pay_system_id)
    payment_class = ResolvePaySystemHandlerService.resolve_paysystem_handler(paysystem_entity.class_name)
    payment_class_obj = payment_class(purchase_output_dto.purchase_id, message.message.chat.id, pay_system_id)
    payment_dict = payment_class_obj.create_payment()

    kb.append([InlineKeyboardButton(text='Ссылка на оплату', url=payment_dict.get("payment_url"))])

    bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
        text='Ссылка на оплату ниже, после оплаты вам придет файл'
    )


@bot.callback_query_handler(func=lambda call: call.data == 'duration')
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
            text=f'До конца вашей подписки осталось {int(delta_time.days)} дней'
        )
    else:
        bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=telebot.types.InlineKeyboardMarkup(keyboard=kb),
            text=sub_expired_text
        )


def bot_polling():
    bot.remove_webhook()

    bot.set_webhook(
        url=f"{WEBHOOK_PATH}/webhook/",
        secret_token=TELEGRAM_SECRET_TOKEN,
    )
    logger.info(f"Webhook = {WEBHOOK_PATH}/webhook/")
