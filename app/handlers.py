from datetime import datetime

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb

from .ai import photo_recognition
from .database.core import (
    get_or_check_user,
    add_user,
    get_leaders,
    insert_completed_task,
    check_completed_task
)
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
async def check_registration(callback: CallbackQuery, state: FSMContext):
    user_result = await get_or_check_user(telegram_id=callback.from_user.id)
    if user_result.get("flag") == True:
        await state.update_data(user=user_result.get("user"))
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
        if weight <= 0 or weight > 150:
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
        if height <= 0 or height > 300:
            await message.answer("Пожалуйста введите рост корректно (см.) 😉")
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
    new_user_result = await get_or_check_user(telegram_id=callback.from_user.id)
    await state.clear()
    await state.update_data(user=new_user_result.get("user"))


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
    task = tasks[task_id]


    test_data = await state.get_data()
    if test_data.get("user") == None:
        user_result = await get_or_check_user(telegram_id=callback.from_user.id)
        await state.update_data(user=user_result.get("user"))

    user = (await state.get_data()).get("user")

    check_task_status = await check_completed_task(task_id=task_id, user_id=user.get("id"))
    if check_task_status == True:
        await callback.message.answer("""
🔔 Ты уже выполнил(а) эту задачу сегодня!
Отличная работа! 💪 Не забывай возвращаться завтра — ежедневный прогресс приносит большие результаты! 🚀😉
""", reply_markup=kb.main_menu_buttons)
        await state.clear()
        return


    await state.update_data(
        task_id=task_id,
        task_name=task.get("name"),
        task_description=task.get("description"),
        task_points=task.get("points"),
    )

    bot_answer = task.get("bot_answer")
    if task.get("type") == "text":
        await state.set_state(TaskStates.waiting_for_text)
    if task.get("type") == "photo":
        await state.set_state(TaskStates.waiting_for_photo)
    await callback.message.answer(bot_answer)


@router.message(TaskStates.waiting_for_photo)
async def photo_task(message: Message, bot: Bot, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, пришлите фото 😊")
        return

    await message.answer("Обработка фото началась...⏳")

    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    data = await state.get_data()

    user = data.get("user")
    task_description = data.get("task_description")
    task_name = data.get("task_name")
    task_id = data.get("task_id")
    task_points = data.get("task_points")
    user_id = user.get("id")

    result = await photo_recognition(
        file_url=file_url,
        task_name=task_name,
        task_description=task_description,
        goal=user.get("goal"),
    )
    
    if result == "False":
        await message.answer("Фото не соответствует заданию, попробуйте ещё раз 😊")
        return

    await insert_completed_task(u_id=user_id, t_id=task_id, adding_points=task_points)
    await message.answer(result, reply_markup=kb.main_menu_buttons, parse_mode="Markdown")
    await state.clear()
    return

@router.message(TaskStates.waiting_for_text)
async def text_task(message: Message, bot: Bot, state: FSMContext):
    pass