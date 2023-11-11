from aiogram import types

def main_menu():
    buttons = [[types.InlineKeyboardButton(text="Посмотреть расписание", callback_data="send_classes")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb