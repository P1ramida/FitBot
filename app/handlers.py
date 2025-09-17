from datetime import datetime

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb

from .ai import photo_recognition
from .database.core import get_or_check_user, add_user, get_leaders
from .texts import (
    WELCOME_TEXT,
    MAIN_MENU_TEXT,
    COMPLETE_REGISTRATION,
    generate_daily_tasks_text,
    generate_leaders_text,
)


router = Router()


class Register(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    goal = State()


class PhotoStates(StatesGroup):
    waiting_for_photo = State()


class TaskStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_text = State()


@router.message(CommandStart())
async def start(message: Message):

    await message.answer(
        WELCOME_TEXT.format(full_name=message.from_user.full_name),
        reply_markup=kb.start_button,
    )


@router.callback_query(F.data == "check_registration")
async def check_registration(callback: CallbackQuery, bot: Bot):
    register_result = await get_or_check_user(callback.from_user.id, flag="check")
    if register_result == True:
        await callback.message.edit_text(
            MAIN_MENU_TEXT.format(full_name=callback.from_user.full_name),
            reply_markup=kb.main_menu_buttons,
        )
    else:
        await callback.message.edit_text(
            """
    Пройдите регистрацию пожалуйста
""",
            reply_markup=kb.start_registration_button,
        )


@router.callback_query(F.data == "start_register")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Register.weight)
    await callback.message.answer("Введите свой вес")


@router.message(Register.weight)
async def get_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 0:
            await message.answer("Пожалуйста введи вес корректно 😉")
            return
        await state.update_data(weight=message.text)
        await state.set_state(Register.height)
        await message.answer("Введите рост")

    except ValueError:
        await message.answer("Пожалуйста введи вес в цифрами например 70 или 85.3 😉")


@router.message(Register.height)
async def get_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        if height <= 0 or height > 140:
            await message.answer("Пожалуйста введите рост корректно 😉")
            return
        await state.update_data(height=message.text)
        await state.set_state(Register.age)
        await message.answer("Введите возраст")

    except ValueError:
        await message.answer("Пожалуйста введите рост в сантиметрах циферками 😉")
        return


@router.message(Register.age)
async def get_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0 or age > 100:
            await message.answer("Пожалуйста введите возраст корректно 😉")
            return
        await state.update_data(age=message.text)
        await state.set_state(Register.gender)
        await message.answer("Укажите свой гендер ☺️", reply_markup=kb.gender_buttons)
    except ValueError:
        await message.answer("Пожалуйста введите возраст в годах циферками 😉")
        return


@router.callback_query(Register.gender, F.data.startswith("gender_"))
async def get_gender(callback: CallbackQuery, state: FSMContext):
    gender_value = callback.data.removeprefix("gender_")
    await state.update_data(gender=gender_value)
    await state.set_state(Register.goal)
    await callback.message.answer(
        "Выбирите цель марафона 😎", reply_markup=kb.goal_buttons
    )


@router.callback_query(Register.goal, F.data.startswith("goal_"))
async def get_goal(callback: CallbackQuery, state: FSMContext):
    goal_value = callback.data.removeprefix("goal_")
    await state.update_data(goal=goal_value)

    data = await state.get_data()
    data["telegram_id"] = callback.from_user.id
    await add_user(data)
    await callback.answer("Марафон начался!")
    await callback.message.answer(
        COMPLETE_REGISTRATION, reply_markup=kb.main_menu_buttons
    )
    await state.clear()


@router.callback_query(F.data == "back_to_main_menu")
async def info(callback: CallbackQuery):
    await callback.message.edit_text(
        MAIN_MENU_TEXT.format(full_name=callback.message.from_user.full_name),
        reply_markup=kb.main_menu_buttons,
    )


@router.callback_query(F.data == "user_raiting")
async def get_raiting(callback: CallbackQuery, bot: Bot):
    leaders_data = await get_leaders()
    leaders = []
    for leader in leaders_data:
        user = await bot.get_chat(leader.get("telegram_id"))
        leaders.append(f"@{user.username} - {leader.get("points")}")

    await callback.message.edit_text(
        generate_leaders_text(leaders), reply_markup=kb.main_menu_buttons
    )


@router.callback_query(F.data == "user_quests")
async def user_quest(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        generate_daily_tasks_text(callback.bot.tasks),
        reply_markup=await kb.generate_task_buttons(callback.bot.tasks),
    )


@router.callback_query(F.data.startswith("task_"))
async def processing_tasks(callback: CallbackQuery, state: FSMContext):
    tasks = callback.bot.tasks
    task_id = int(callback.data.removeprefix("task_"))
    await state.update_data(task_id=task_id)

    task = tasks[task_id]
    bot_answer = task.get("bot_answer")
    if task.get("type") == "text":
        await state.set_state(TaskStates.waiting_for_text)
    if task.get("type") == "photo":
        await state.set_state(TaskStates.waiting_for_photo)
    await callback.message.answer(bot_answer)


@router.message(TaskStates.waiting_for_photo)
async def task_text_answer(message: Message, bot: Bot, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, пришлите фото 😊")
        return
    await message.answer("Обработка фото началась...⏳")
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    result = await photo_recognition(file_url)
    if result == "False":
        await message.answer("Пожалуйста, пришлите фото еды 😊")
        return
    await message.answer(result, reply_markup=kb.main_menu_buttons)
    await state.clear()
