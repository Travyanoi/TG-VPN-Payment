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
regex_for_separate_octets = re.compile(r"(\d+).(\d+).(\d+).(\d+)(\S+)")

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


def conf_file_formatter():
    os.chdir("TG-VPN-Payment")
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
        
        for client_name, client_info in data["clients"].items():
            if client_info["enable"] is True:
                address = client_info["address"]
                output_file.write(f"#{client_name}\n"
                                f"[Peer]\n"
                                f"Publickey = {server_pubkey}\n"
                                f"AllowedIPs = {address}\n\n")
            else:
                continue
            
    stream.close()       
    os.chdir("/home/ivan")


def json_formatter(chat_id: UserInfo.chat_id, duration_of_sub: str):
    os.chdir("TG-VPN-Payment")
    data = json.load(open('data.json'))

    username: UserInfo = UserInfo.get(UserInfo.chat_id == chat_id)
    
    subprocess.check_output(f"wg genkey | tee {username.first_name}_privatekey |"
                            f" wg pubkey | tee {username.first_name}_publickey",
                            shell=True).decode("utf-8").strip()
    
    with open(f"{username.first_name}_privatekey") as privkey:
        with open(f"{username.first_name}_publickey") as pubkey:
            created_at_time = datetime.datetime.now()
            
            expiration_date = created_at_time + datetime.timedelta(days=30 * int(duration_of_sub))
            
            name_last_client, info_last_client = list(data["clients"].items())[-1]
            
            temp_addr_array = re.split(regex_for_separate_octets, info_last_client["address"]) #parse full addr and concatenate last octet
            temp_addr_array[4] = (int(temp_addr_array[4]) + 1)
            address_for_user = f"{temp_addr_array[1]}.{temp_addr_array[2]}.{temp_addr_array[3]}.{temp_addr_array[4]}/32"
            
            data["clients"].update({f"{username.first_name}": {"address": address_for_user,
                                                               "publickey": pubkey.read().strip(),
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
    conf_file_formatter()


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.InlineKeyboardButton("1 Месяц", callback_data="1_month_sub")],
        [types.InlineKeyboardButton("4 Месяца", callback_data="4_months_sub")],
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


@dp.callback_query_handler(text=["1_month_sub", "4_months_sub", "6_months_sub", "12_months_sub"])
async def payment_cmd(message: types.CallbackQuery):
    duration_of_subscription = re.split(regex_for_digit, message.data)
    await bot.send_message(chat_id=message.message.chat.id, text="Сейчас все сделаю...")

    json_formatter(message.message.chat.id, str(duration_of_subscription[1]))


async def main():
    db.create_tables([UserInfo])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
