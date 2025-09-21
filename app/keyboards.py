from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Начать", callback_data="check_registration"),
        ]
    ]
)

start_registration_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔐 Пройти регистрацию", callback_data="start_register"
            ),
        ]
    ]
)

back_to_main_button = [
    InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main_menu")
]

goal_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🧘‍♂️ Похудеть", callback_data="goal_1"),
            InlineKeyboardButton(text="💪 Набрать", callback_data="goal_2"),
        ]
    ]
)

gender_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='♂️ Мужчина', callback_data='gender_1'),
            InlineKeyboardButton(text='♀️ Женищна', callback_data='gender_2')
        ]
    ]
)

main_menu_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📋 Задания", callback_data="user_quests")],
        [InlineKeyboardButton(text="🏆 Достижения", callback_data="user_achive")],
        [InlineKeyboardButton(text="📊 Рейтинг", callback_data="user_raiting")],
        [InlineKeyboardButton(text="📒 Инструкции", callback_data="user_instruction")],
    ]
)


async def generate_task_buttons(tasks: dict) -> InlineKeyboardMarkup:
    buttons = []
    for task_id, task_data in tasks.items():
        if task_data.get("is_active"):
            text = task_data.get("name")
            buttons.append([InlineKeyboardButton(text=text, callback_data="task_" + str(task_id))])

    buttons.append(back_to_main_button)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


