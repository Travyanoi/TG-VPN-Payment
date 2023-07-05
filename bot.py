import asyncio
import os
import json
import datetime
import subprocess

import peewee
from peewee import Model, CharField

from aiogram.dispatcher.filters import Command
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

db = peewee.SqliteDatabase("UserInfo.sqlite")


class UserInfo(Model):
    chat_id = CharField(max_length=64, primary_key=True)
    first_name = CharField(max_length=32)
    last_name = CharField(max_length=32)
    username = CharField(max_length=32)

    class Meta:
        database = db


load_dotenv()

bot = Bot(token=os.environ.get("BOT_TOKEN"))

dp = Dispatcher(bot)


def json_formatter(chat_id: UserInfo.chat_id):
    data = json.load(open('data.json'))

    username: UserInfo = UserInfo.get(UserInfo.chat_id == chat_id)

    subprocess.check_output(f"wg genkey & tee {username.first_name}_privatekey &"
                            f"wg pubkey & tee {username.first_name}_publickey",
                            shell=True).decode("utf-8").strip()

    with open(f"{username}_privatekey") as privkey:
        with open(f"{username}_publickey") as pubkey:
            data["clients"].update({f"{username}": {"publickey": pubkey.read().strip(),
                                                    "privatekey": f"{privkey.read().strip()}",
                                                    "created_at": datetime.datetime.now(),
                                                    "enable": True
                                                    }})

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.InlineKeyboardButton("1 Месяц", callback_data="1_month_sub")],
        [types.InlineKeyboardButton("6 Месяцев", callback_data="6_months_sub")],
        [types.InlineKeyboardButton("12 Месяцев", callback_data="12_months_sub")],
    ]
    UserInfo.get_or_create(chat_id=message.chat.id, defaults={"first_name": message.chat.first_name or "",
                                                              "last_name": message.chat.last_name or "",
                                                              "username": message.chat.username or ""})

    await bot.send_message(chat_id=message.chat.id, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                           text="Привет! Через данного бота у вас есть возможность "
                                "приобрести впн по довольно низкой цене!\nПожалуйста, выберите продолжительность "
                                "подписки!")


@dp.callback_query_handler(text=["1_month_sub", "6_months_sub", "12_months_sub"])
async def payment_cmd(message: types.CallbackQuery):
    await bot.send_message(chat_id=message.message.chat.id, text="Сейчас все сделаю...")

    json_formatter(message.message.chat.id)


async def main():
    db.create_tables([UserInfo])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
