import os
import datetime
import re

from io import BytesIO

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import BufferedInputFile

from dotenv import load_dotenv
from wireguard_tools import WireguardKey

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.bot.models import UserInfo, InfoForConfFile, ServerConfInfo
from settings.settings import WG_CONF_ROOT, BOT_SECRET_TOKEN, WEBHOOK_PATH, TELEGRAM_SECRET_TOKEN

regex_for_digit = re.compile(r"(\d+)")

bot = Bot(token=BOT_SECRET_TOKEN, parse_mode=ParseMode.HTML)

router = Router(name=__name__)

dp = Dispatcher()


async def send_conf_file(chat_id: UserInfo.chat_id, message_id: int):
    byte_string = await conf_file_for_user(chat_id)

    file = BufferedInputFile(file=byte_string.getvalue(), filename="WireGuard.conf")

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.send_document(chat_id=chat_id, document=file)

async def check_sub():
    kb = [
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
    ]

    async for client_subscription in InfoForConfFile.objects.aiterator():
        if not client_subscription.enable:
            continue

        expiration_date = client_subscription.expires_at
        now_date = datetime.datetime.now(tz=datetime.UTC)
        delta_time = expiration_date - now_date

        if delta_time.days == 0:
            await bot.send_message(
                chat_id=client_subscription.client_id,
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                text="Ваша подписка скоро закончится, вы можете продлить ее нажав кнопку 'Продлить подписку'"
            )

        elif delta_time.days < 0:
            client_subscription.enable = False
            await client_subscription.save()

            await bot.send_message(
                chat_id=client_subscription.client_id,
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                text="Ваша подписка закончилась, вы можете продлить ее нажав кнопку 'Продлить подписку'"
            )

    await conf_file_formatter()


async def resub(chat_id: UserInfo.chat_id, resub_time_in_months: str):

    client: InfoForConfFile = await InfoForConfFile.objects.aget(chat_id=chat_id)

    expiration_date = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=30 * int(resub_time_in_months))
    client.expires_at = expiration_date
    client.enable = True
    await client.asave()


async def conf_file_for_user(chat_id: UserInfo.chat_id) -> BytesIO:

    db_conf_info: InfoForConfFile = await InfoForConfFile.objects.aget(chat_id_id=chat_id)
    db_server_info: ServerConfInfo = await ServerConfInfo.objects.afirst()

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


async def conf_file_formatter():

    with open(f"{WG_CONF_ROOT}\wg0.conf", 'w') as output_file:
        server_data = await ServerConfInfo.objects.afirst()

        output_file.write(f"[Interface]\n"
                          f"PrivateKey = {server_data.privatekey}\n"
                          f"Address = 10.10.0.1/24\n"
                          f"ListenPort = 51830\n"
                          f"PostUp = /etc/wireguard/postup.sh\n"
                          f"PostDown = /etc/wireguard/postdown.sh\n\n")

        async for client_info in InfoForConfFile.objects.aiterator():
            if not client_info.enable:
                continue

            output_file.write(f"#{client_info.first_name.encode('utf-8').decode()}\n"
                              f"[Peer]\n"
                              f"Publickey = {client_info.publickey}\n"
                              f"AllowedIPs = {client_info.address}\n\n")


async def conf_db_formatter(chat_id: UserInfo.chat_id, duration_of_sub: str):

    username: UserInfo = await UserInfo.objects.aget(chat_id=chat_id)
    private_key = WireguardKey.generate()
    public_key = private_key.public_key()

    start_at_time = datetime.datetime.now(tz=datetime.UTC)

    expiration_date = start_at_time + datetime.timedelta(days=30 * int(duration_of_sub))

    last_octet = await InfoForConfFile.objects.acount() + 2
    address_for_user = f"10.0.0.{last_octet}/32"

    await InfoForConfFile.objects.aget_or_create(
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


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(text="Купить подписку", callback_data="buy_sub")],
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
        [types.InlineKeyboardButton(text="Узнать продолжительность купленной подписки", callback_data="duration")],
    ]

    await UserInfo.objects.aget_or_create(
        chat_id=message.chat.id,
        defaults={
            "first_name": message.chat.first_name or "",
            "last_name": message.chat.last_name or "",
            "username": message.chat.username or ""
        }
    )

    await bot.send_message(
        chat_id=message.chat.id,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        text="Привет! Через данного бота у вас есть возможность приобрести VPN по низкой цене!"
    )


@router.callback_query(F.data == "buy_sub")
async def buy_sub_cmd(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(text="1 Месяц", callback_data="1_month_sub")],
        [types.InlineKeyboardButton(text="4 Месяца", callback_data="4_month_sub")],
        [types.InlineKeyboardButton(text="6 Месяцев", callback_data="6_month_sub")],
        [types.InlineKeyboardButton(text="12 Месяцев", callback_data="12_month_sub")],
    ]
    await bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        text="Пожалуйста, выберите продолжительность подписки!"
    )


@router.callback_query(F.data.endswith('_month_sub'))
async def payment_cmd(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
        [types.InlineKeyboardButton(text="Узнать продолжительность купленной подписки", callback_data="duration")],
    ]
    duration_of_subscription = re.split(regex_for_digit, message.data)
    await bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        text="Сейчас все сделаю..."
    )

    await conf_db_formatter(message.message.chat.id, str(duration_of_subscription[1]))
    await conf_file_formatter()
    await send_conf_file(message.message.chat.id, message.message.message_id)

    await bot.send_message(
        chat_id=message.message.chat.id,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        text="Это ваш конфигурационный файл для WireGuard, чтобы его активировать, "
             "нужно выбрать данный файл в приложении WireGuard в меню 'выбрать туннель'"
    )


@router.callback_query(F.data == "rebuild_conf_file")
async def rebuild_conf_cmd(message: types.CallbackQuery):

    kb = [
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
        [types.InlineKeyboardButton(text="Узнать продолжительность купленной подписки", callback_data="duration")],
    ]

    client = await InfoForConfFile.objects.aget(chat_id=message.message.chat.id)

    if client.enable is True:
        await send_conf_file(message.message.chat.id, message.message.message_id)

        await bot.send_message(
            chat_id=message.message.chat.id,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
            text="Это ваш конфигурационный файл для WireGuard, чтобы его активировать, "
                 "нужно выбрать данный файл в приложении WireGuard в меню 'выбрать туннель'"
        )
    else:
        await bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
            text="К сожалению, ваша подписка кончилась!\n"
                 "Вы можете ее продлить с помощью кнопки 'Продлить продписку'!"
        )


@router.callback_query(F.data == "duration")
async def duration_sub_cmd(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
        [types.InlineKeyboardButton(text="Отправить конфигурационный файл", callback_data="rebuild_conf_file")],
        [types.InlineKeyboardButton(text="Узнать продолжительность купленной подписки", callback_data="duration_sub")],
    ]


    client = await InfoForConfFile.objects.aget(chat_id=message.message.chat.id)

    expiration_date = client.expires_at

    now_date = datetime.datetime.now(tz=datetime.UTC)
    delta_time = expiration_date - now_date
    if int(delta_time.days) > 0:
        await bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
            text=f"До конца вашей подписки осталось {int(delta_time.days)} дней"
        )
    else:
        await bot.edit_message_text(
            chat_id=message.message.chat.id,
            message_id=message.message.message_id,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
            text="Ваша подписка закончилась! Вы можете продлить ее с помощью кнопки 'Продлить подписку'!"
        )


@router.callback_query(F.data == "resub")
async def resub_cmd(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(text="1 Месяц", callback_data="1_month_resub")],
        [types.InlineKeyboardButton(text="4 Месяца", callback_data="4_month_resub")],
        [types.InlineKeyboardButton(text="6 Месяцев", callback_data="6_month_resub")],
        [types.InlineKeyboardButton(text="12 Месяцев", callback_data="12_month_resub")],
    ]
    await bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        text="Пожалуйста, выберите продолжительность продления подписки!"
    )


@router.callback_query(F.data.endswith('_month_resub'))
async def resub_payment(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
        [types.InlineKeyboardButton(text="Отправить конфигурационный файл", callback_data="rebuild_conf_file")],
        [types.InlineKeyboardButton(text="Узнать продолжительность купленной подписки", callback_data="duration_sub")],
    ]

    duration_of_subscription = re.split(regex_for_digit, message.data)

    await resub(message.message.chat.id, duration_of_subscription[1])
    await bot.edit_message_text(
        chat_id=message.message.chat.id,
        message_id=message.message.message_id,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        text="Вы успешно продлили подписку!\nВы можете использовать старый конфигурационный файл,"
             "если вы его утеряли, можете нажать кнопку 'Отправить конфигурационный файл'!"
    )

async def on_startup():
    await bot.delete_webhook()

    try:
        await bot.set_webhook(url=f"{WEBHOOK_PATH}/webhook")

        await bot.send_message(chat_id=5709145109, text='Бот запущен!')
        await bot.send_message(chat_id=5709145109, text=f'Webhook зарегистрирован по адресу {WEBHOOK_PATH}/webhook')
    except Exception as e:
        await bot.send_message(chat_id=5709145109, text=f'Что-то поломалось брат\n{e}')


dp.include_router(router)

async def BotPolling():
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{WEBHOOK_PATH}/webhook/")
    #dp.startup.register(on_startup)

