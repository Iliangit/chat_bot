from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio
import sqlite3
from kb import main_menu
from config import TOKEN, admins_id

dp = Dispatcher()

db = sqlite3.connect('raspisanie.db', check_same_thread=False)
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS classes(name TEXT, monday TEXT, tuesday TEXT, wednesday TEXT, thursday TEXT, friday TEXT)")
db.commit()

class AddClass(StatesGroup):
    name = State()
    monday = State()
    tuesday = State()
    wednesday = State()
    thursday = State()
    friday = State()


@dp.callback_query(F.data == "yes_updates")
async def insert_data(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    buttons = [[types.InlineKeyboardButton(text="Добавить расписание", callback_data="add_class")]]
    mar = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    state_data = await state.get_data()

    cur.execute("INSERT INTO classes VALUES (?, ?, ?, ?, ?, ?)", (state_data["name"], state_data["monday"], state_data["tuesday"], state_data['wednesday'], state_data["thursday"], state_data['friday']))
    db.commit()
    await call.message.answer("Данные занесены в базу данных", reply_markup=mar)
    await state.clear()


@dp.callback_query(F.data == "add_class")
async def add_class(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Введите название класса в формате '10 A' ")
    await state.set_state(AddClass.name)

@dp.message(AddClass.name)
async def add_class(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    class_name = await state.get_data()
    await message.answer(f"Введите расписание {class_name['name'].split(' ')[0]}-ого {class_name['name'].split(' ')[1]} на понедельник\n(В формате: Математика, Русский язык, ...)")
    await state.set_state(AddClass.monday)


@dp.message(AddClass.monday)
async def add_class(message: types.Message, state: FSMContext):
    await state.update_data(monday=message.text)
    class_name = await state.get_data()
    await message.answer(f"Введите расписание {class_name['name'].split(' ')[0]}-ого {class_name['name'].split(' ')[1]} на вторник\n(В формате: Математика, Русский язык, ...)")
    await state.set_state(AddClass.tuesday)


@dp.message(AddClass.tuesday)
async def add_class(message: types.Message, state: FSMContext):
    await state.update_data(tuesday=message.text)
    class_name = await state.get_data()
    await message.answer(f"Введите расписание {class_name['name'].split(' ')[0]}-ого {class_name['name'].split(' ')[1]} на среду\n(В формате: Математика, Русский язык, ...)")
    await state.set_state(AddClass.wednesday)


@dp.message(AddClass.wednesday)
async def add_class(message: types.Message, state: FSMContext):
    await state.update_data(wednesday=message.text)
    class_name = await state.get_data()
    await message.answer(f"Введите расписание {class_name['name'].split(' ')[0]}-ого {class_name['name'].split(' ')[1]} на четверг\n(В формате: Математика, Русский язык, ...)")
    await state.set_state(AddClass.thursday)


@dp.message(AddClass.thursday)
async def add_class(message: types.Message, state: FSMContext):
    await state.update_data(thursday=message.text)
    class_name = await state.get_data()
    await message.answer(f"Введите расписание {class_name['name'].split(' ')[0]}-ого {class_name['name'].split(' ')[1]} на пятницу\n(В формате: Математика, Русский язык, ...)")
    await state.set_state(AddClass.friday)


@dp.message(AddClass.friday)
async def add_class(message: types.Message, state: FSMContext):
    buts = [[types.InlineKeyboardButton(text="Да", callback_data="yes_updates"), types.InlineKeyboardButton(text="Нет", callback_data="no_updates")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buts)
    await state.update_data(friday=message.text)
    class_name = await state.get_data()
    await message.answer(f"{class_name['name']}\n{class_name['monday']}\n{class_name['tuesday']}\n{class_name['wednesday']}\n{class_name['thursday']}\n{class_name['friday']}\n\nСохранить изменения?", reply_markup=kb)


@dp.callback_query(F.data == "back_main_menu")
async def back_main_menu(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(text="Вы в главном меню", reply_markup=main_menu())


@dp.message((F.text == "/adminpanel") & (F.from_user.id in admins_id))
async def login(message: types.Message):
    buttons = [[types.InlineKeyboardButton(text="Добавить расписание", callback_data="add_class")]]
    mar = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Вы в панели администратора", reply_markup=mar)


def create_but_class():
    classes = [types.InlineKeyboardButton(text=item[0], callback_data=item[0]) for num, item in enumerate(cur.execute("SELECT * FROM classes").fetchall())]

    split_size = 3
    buttons = [classes[i:i + split_size] for i in range(0, len(classes), split_size)]
    buttons.append([types.InlineKeyboardButton(text="Назад", callback_data="back_main_menu")])

    return buttons


@dp.callback_query(F.data == "send_classes")
async def send_classes(call: types.CallbackQuery):
    await call.message.delete()
    mar = types.InlineKeyboardMarkup(inline_keyboard=create_but_class())
    await call.message.answer(text="Расписание:", reply_markup=mar)


@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("text", reply_markup=main_menu())


@dp.callback_query()
async def send_schedule(call: types.CallbackQuery):
    if call.data in [name[0] for name in cur.execute("SELECT * FROM classes").fetchall()]:
        await call.message.delete()
        but = [[types.InlineKeyboardButton(text="Понедельник", callback_data=f"monday_{call.data}")], [types.InlineKeyboardButton(text="Вторник", callback_data=f"tuesday_{call.data}")], [types.InlineKeyboardButton(text="Среда", callback_data=f"wednesday_{call.data}")], [types.InlineKeyboardButton(text="Четверг", callback_data=f"thursday_{call.data}")], [types.InlineKeyboardButton(text="Пятница", callback_data=f"friday_{call.data}")]]
        kb = types.InlineKeyboardMarkup(inline_keyboard=but)

        await call.message.answer("Выберете день", reply_markup=kb)

    if call.data.split("_")[0] in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        but = [[types.InlineKeyboardButton(text="Назад", callback_data="send_classes")]]
        kb = types.InlineKeyboardMarkup(inline_keyboard=but)
        await call.message.delete()
        school_class = cur.execute(f"SELECT {call.data.split('_')[0]} FROM classes WHERE name = (?)", (call.data.split("_")[1],)).fetchone()
        await call.message.answer(text=f'{call.data.split("_")[1]}\n' + school_class[0].replace(", ", "\n"), reply_markup=kb)


async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())