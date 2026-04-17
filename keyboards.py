from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📸 Анализ еды"), KeyboardButton(text="💪 Тренировка")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🎯 Моя цель")],
            [KeyboardButton(text="💧 Вода"), KeyboardButton(text="⚖️ Мой вес")],
        ],
        resize_keyboard=True
    )

def goals_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Набор массы", callback_data="goal_mass")],
        [InlineKeyboardButton(text="🔥 Похудение", callback_data="goal_loss")],
        [InlineKeyboardButton(text="⚡ Поддержание формы", callback_data="goal_keep")],
    ])

def water_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🥤 200 мл", callback_data="water_200"),
            InlineKeyboardButton(text="🥤 300 мл", callback_data="water_300"),
        ],
        [
            InlineKeyboardButton(text="🍶 500 мл", callback_data="water_500"),
            InlineKeyboardButton(text="🍶 750 мл", callback_data="water_750"),
        ],
        [InlineKeyboardButton(text="💧 1000 мл", callback_data="water_1000")],
    ])

def workout_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено!", callback_data="workout_done")],
        [InlineKeyboardButton(text="🔄 Другую тренировку", callback_data="workout_new")],
    ])