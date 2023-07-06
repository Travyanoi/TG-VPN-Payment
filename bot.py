import asyncio
import os
import json
import datetime
import subprocess
import re

import peewee
from peewee import Model, CharField

from aiogram.dispatcher.filters import Command
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

db = peewee.SqliteDatabase("TG-VPN-Payment/UserInfo.sqlite")

regex_for_digit = re.compile(r"(\d+)")

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


def json_formatter(chat_id: UserInfo.chat_id, duration_of_sub: str):
    os.chdir("TG-VPN-Payment")
    data = json.load(open('data.json'))

    username: UserInfo = UserInfo.get(UserInfo.chat_id == chat_id)

    print(duration_of_sub)
    subprocess.check_output(f"wg genkey | tee {username.first_name}_privatekey |"
                            f" wg pubkey | tee {username.first_name}_publickey",
                            shell=True).decode("utf-8").strip()
    
    with open(f"{username.first_name}_privatekey") as privkey:
        with open(f"{username.first_name}_publickey") as pubkey:
            created_at_time = datetime.datetime.now()
            expiration_date = created_at_time + datetime.timedelta(days=30 * int(duration_of_sub))
            
            data["clients"].update({f"{username.first_name}": {"publickey": pubkey.read().strip(),
                                                    "privatekey": f"{privkey.read().strip()}",
                                                    "created_at": f"{created_at_time}",
                                                    "expiration_of_sub_date" : f"{expiration_date}",
                                                    "enable": True
                                                    }})
            
            os.remove(f"{privkey.name}")
            os.remove(f"{pubkey.name}")

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.chdir("/home/ivan")


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
                                "приобрести VPN по низкой цене!\nПожалуйста, выберите продолжительность "
                                "подписки!")


@dp.callback_query_handler(text=["1_month_sub", "6_months_sub", "12_months_sub"])
async def payment_cmd(message: types.CallbackQuery):
    duration_of_subscription = re.split(regex_for_digit, message.data)
    await bot.send_message(chat_id=message.message.chat.id, text="Сейчас все сделаю...")

    json_formatter(message.message.chat.id, str(duration_of_subscription[1]))


async def main():
    db.create_tables([UserInfo])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
