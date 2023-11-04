import os
import json
import datetime
import re

from io import BytesIO

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import FSInputFile, BufferedInputFile

from dotenv import load_dotenv
from wireguard_tools import WireguardKey

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.bot.models import UserInfo, InfoForConfFile, ServerConfInfo

regex_for_digit = re.compile(r"(\d+)")

load_dotenv()

bot = Bot(token=os.environ.get("BOT_TOKEN"))

router = Router(name=__name__)

dp = Dispatcher()



async def send_conf_file(chat_id: UserInfo.chat_id, message_id: int):
    byte_string = await conf_file_for_user(chat_id)

    file = BufferedInputFile(file=byte_string.getvalue(), filename="WireGuard.conf")

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.send_document(chat_id=chat_id, document=file)


async def check_sub():
    stream = open("data.json")
    data = json.load(stream)
    kb = [
        [types.InlineKeyboardButton(text="Продлить подписку", callback_data="resub")],
    ]
    clients = await InfoForConfFile.objects.all()
    for client_id, client_info in data["clients"].items():
        if client_info["enable"] is False:
            continue

        expiration_date = datetime.datetime.strptime(
            client_info["expiration_of_sub_date"],
            "%Y-%m-%d %H:%M:%S.%f"
        )

        now_date = datetime.datetime.now()
        delta_time = expiration_date - now_date

        if delta_time.days == 0:
            await bot.send_message(
                chat_id=client_id,
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                text="Ваша подписка скоро закончится, вы можете продлить ее нажав кнопку 'Продлить подписку'"
            )

        elif delta_time.days < 0:
            data["clients"][client_id]["enable"] = False

            await bot.send_message(
                chat_id=client_id,
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                text="Ваша подписка закончилась, вы можете продлить ее нажав кнопку 'Продлить подписку'"
            )

        else:
            continue

    stream.close()

    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    conf_file_formatter()


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
        f"PublicKey = {db_server_info.server_publickey}\n"
        "AllowedIPs = 0.0.0.0/0\n"
        f"Endpoint = {db_server_info.server_end_point}\n"
        "PersistentKeepalive = 20".encode('utf-8')
    )

    return file


def conf_file_formatter():
    stream = open('data.json')
    data = json.load(stream)

    with open("wg0.conf", 'w') as output_file:
        server_privkey = data["server"]["server_privatekey"]
        server_pubkey = data["server"]["server_publickey"]

        output_file.write(f"[Interface]\n"
                          f"PrivateKey = {server_privkey}\n"
                          f"Address = 10.10.0.1/24\n"
                          f"ListenPort = 51830\n"
                          f"PostUp = /etc/wireguard/postup.sh\n"
                          f"PostDown = /etc/wireguard/postdown.sh\n\n")

        clients = InfoForConfFile.objects.filter(enable=True).all

        for client_id, client_info in data["clients"].items():
            if client_info["enable"] is True:
                address = client_info["address"]
                client_name = client_info["first_name"]

                output_file.write(f"#{client_name}\n"
                                  f"[Peer]\n"
                                  f"Publickey = {server_pubkey}\n"
                                  f"AllowedIPs = {address}\n\n")
            else:
                continue

    stream.close()


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
    #conf_file_formatter()
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


async def BotPolling():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_sub, "interval", seconds=300)
    scheduler.start()
    dp.include_router(router)
    await dp.start_polling(bot)
