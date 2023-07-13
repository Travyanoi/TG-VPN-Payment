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

from apscheduler.schedulers.asyncio import AsyncIOScheduler

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

async def check_sub():
    os.chdir("TG-VPN-Payment")
    stream = open("data.json")
    data = json.load(stream)
    kb = [
        [types.InlineKeyboardButton("Продлить подписку", callback_data="renew_sub")],
    ]

    for client_name, client_info in data["clients"].items():
        if client_info["enable"] is False:
            continue
        
        expiration_date = datetime.datetime.strptime(client_info["expiration_of_sub_date"], "%Y-%m-%d %H:%M:%S.%f")
        now_date = datetime.datetime.now()
        delta_time = expiration_date.day - now_date.day
        if delta_time == 0:
            await bot.send_message(chat_id=client_info["chat_id"], reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                             text="Ваша подписка скоро закончится, вы можете продлить ее нажав кнопку 'Продлить подписку'")
        elif delta_time < 0:
            data["clients"][client_name]["enable"] = False
            await bot.send_message(chat_id=client_info["chat_id"], reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                             text="Ваша подписка закончилась, вы можете продлить ее нажав кнопку 'Продлить подписку'")
        else:
            continue

    stream.close()

    with open('data.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    conf_file_formatter()
    
    os.chdir("/home/ivan")
    

def conf_file_for_user(chat_id: UserInfo.chat_id):   
    stream = open('data.json')
    data = json.load(stream)
    
    db_username_info: UserInfo = UserInfo.get(UserInfo.chat_id == chat_id)
    js_username_info = data["clients"][db_username_info.first_name]
    
    with open(f"WireGuard.conf", 'w') as file:
        user_private_key = js_username_info["privatekey"]
        user_address = js_username_info["address"]
        file.write(f"[Interface]\n"
                   f"Privatekey = {user_private_key}\n"
                   f"Address = {user_address}\n"
                   f"DNS = 8.8.8.8\n\n")
        
        server_public_key = data["server"]["server_publickey"]
        server_end_point = data["server"]["server_end_point"]
        file.write(f"[Peer]\n"
                   f"PublicKey = {server_public_key}\n"
                   f"AllowedIPs = 0.0.0.0/0\n"
                   f"Endpoint = {server_end_point}\n"
                   f"PersistentKeepalive = 20")
        
    stream.close()
    


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


def json_formatter(chat_id: UserInfo.chat_id, duration_of_sub: str):
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
            
            data["clients"].update({f"{username.first_name}": {"chat_id": chat_id,
                                                               "address": address_for_user,
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
    


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.InlineKeyboardButton("Купить подписку", callback_data="buy_sub")],
        [types.InlineKeyboardButton("Продлить подписку", callback_data="renew_sub")],
        [types.InlineKeyboardButton("Узнать продолжительность купленной подписки", callback_data="duration_sub")],
    ]
    
    UserInfo.get_or_create(chat_id=message.chat.id, defaults={"first_name": message.chat.first_name or "",
                                                              "last_name": message.chat.last_name or "",
                                                              "username": message.chat.username or ""})

    await bot.send_message(chat_id=message.chat.id, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                           text="Привет! Через данного бота у вас есть возможность "
                                "приобрести VPN по низкой цене!")


@dp.callback_query_handler(text="buy_sub")
async def buy_sub_cmd(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton("1 Месяц", callback_data="1_month_sub")],
        [types.InlineKeyboardButton("4 Месяца", callback_data="4_months_sub")],
        [types.InlineKeyboardButton("6 Месяцев", callback_data="6_months_sub")],
        [types.InlineKeyboardButton("12 Месяцев", callback_data="12_months_sub")],
    ]
    await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                                text="Пожалуйста, выберите продолжительность подписки!")


@dp.callback_query_handler(text=["1_month_sub", "4_months_sub", "6_months_sub", "12_months_sub"])
async def payment_cmd(message: types.CallbackQuery):
    kb = [
        [types.InlineKeyboardButton("Продлить подписку", callback_data="renew_sub")],
        [types.InlineKeyboardButton("Узнать продолжительность купленной подписки", callback_data="duration_sub")],
    ]
    os.chdir("TG-VPN-Payment")
    duration_of_subscription = re.split(regex_for_digit, message.data)
    await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text="Сейчас все сделаю...")

    json_formatter(message.message.chat.id, str(duration_of_subscription[1]))
    conf_file_for_user(message.message.chat.id)
    conf_file_formatter()

    with open("WireGuard.conf", 'rb') as file:
        await bot.delete_message(chat_id=message.message.chat.id, message_id=message.message.message_id)
        
        await bot.send_document(chat_id=message.message.chat.id, document=file)
                            
        await bot.send_message(chat_id=message.message.chat.id, 
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                               text="Это ваш конфигурационный файл для WireGuard, чтобы его активировать, " 
                                "нужно выбрать данный файл в приложении WireGuard в меню 'выбрать туннель'")
    os.chdir("/home/ivan")


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_sub, "interval", hours=1)
    scheduler.start()
    db.create_tables([UserInfo])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
