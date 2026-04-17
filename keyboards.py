from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📸 Анализ еды"), KeyboardButton(text="💪 Тренировка")],
            [KeyboardButton(text="📊 Моя статистика"), KeyboardButton(text="🎯 Моя цель")],
        ],
        resize_keyboard=True
    )

def goals_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Набор массы", callback_data="goal_mass")],
        [InlineKeyboardButton(text="🔥 Похудение", callback_data="goal_loss")],
        [InlineKeyboardButton(text="⚡ Поддержание формы", callback_data="goal_keep")],
    ])