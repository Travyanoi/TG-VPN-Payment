from telebot.types import InlineKeyboardButton

global_kb = \
[
    [InlineKeyboardButton(text="Купить подписку", callback_data="buy_sub")], #0
    [InlineKeyboardButton(text="Продлить подписку", callback_data="resub")], #1
    [InlineKeyboardButton(text="Узнать продолжительность купленной подписки", callback_data="duration")], #2
    [InlineKeyboardButton(text="1 Месяц", callback_data="1_month_sub")], #3
    [InlineKeyboardButton(text="4 Месяца", callback_data="4_month_sub")], #4
    [InlineKeyboardButton(text="6 Месяцев", callback_data="6_month_sub")], #5
    [InlineKeyboardButton(text="12 Месяцев", callback_data="12_month_sub")], #6
    [InlineKeyboardButton(text="1 Месяц", callback_data="1_month_resub")], #7
    [InlineKeyboardButton(text="4 Месяца", callback_data="4_month_resub")], #8
    [InlineKeyboardButton(text="6 Месяцев", callback_data="6_month_resub")], #9
    [InlineKeyboardButton(text="12 Месяцев", callback_data="12_month_resub")], #10
    [InlineKeyboardButton(text="Отправить конфигурационный файл", callback_data="rebuild_conf_file")] #11
]