import asyncio
import os
from google import genai
from google.genai import types
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
from database import (init_db, get_or_create_user, set_goal,
                      get_stats, add_calories, add_water,
                      add_weight, get_weight_history)
from keyboards import main_menu, goals_keyboard, water_keyboard, workout_keyboard

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash-lite"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

DAILY_NORM = {"calories": 2000, "protein": 150, "fat": 65, "carbs": 250, "water": 2000}


def progress_bar(current: int, total: int, length: int = 8) -> str:
    current = int(current) if current else 0
    filled = int((current / total) * length) if total > 0 else 0
    filled = min(filled, length)
    bar = "🟩" * filled + "⬜" * (length - filled)
    percent = min(int((current / total) * 100), 100) if total > 0 else 0
    return f"{bar} {percent}%"


@dp.message(CommandStart())
async def start(message: Message):
    get_or_create_user(message.from_user.id, message.from_user.first_name)
    await message.answer(
        f"👋 Привет, *{message.from_user.first_name}*!\n\n"
        f"Я твой персональный AI фитнес-тренер 🤖\n\n"
        f"*Что я умею:*\n"
        f"📸 Анализирую еду на фото → КБЖУ\n"
        f"💪 Составляю программы тренировок\n"
        f"📊 Веду дневник питания и воды\n"
        f"⚖️ Отслеживаю динамику веса\n"
        f"🎯 Подбираю план под твою цель\n\n"
        f"Выбери действие в меню ниже 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


@dp.message(F.text == "🎯 Моя цель")
async def goal_menu(message: Message):
    user = get_stats(message.from_user.id)
    current = user[2] if user else "не указана"
    await message.answer(
        f"🎯 *Текущая цель:* {current}\n\nВыбери новую цель:",
        parse_mode="Markdown",
        reply_markup=goals_keyboard()
    )


@dp.callback_query(F.data.startswith("goal_"))
async def set_goal_handler(callback: CallbackQuery):
    goals = {
        "goal_mass": "🏋️ Набор массы",
        "goal_loss": "🔥 Похудение",
        "goal_keep": "⚡ Поддержание формы"
    }
    goal = goals[callback.data]
    set_goal(callback.from_user.id, goal)
    await callback.message.edit_text(
        f"✅ Цель установлена: *{goal}*\n\n"
        f"Теперь отправь фото еды или запроси тренировку!",
        parse_mode="Markdown"
    )


@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    user = get_stats(message.from_user.id)
    if not user:
        await message.answer("Сначала напиши /start!")
        return

    name, goal = user[1], user[2]
    cal = int(user[3]) if user[3] else 0
    prot = int(user[4]) if user[4] else 0
    fat = int(user[5]) if user[5] else 0
    carbs = int(user[6]) if user[6] else 0
    water = int(user[7]) if user[7] else 0

    await message.answer(
        f"📊 *Статистика за сегодня*\n"
        f"👤 {name} • 🎯 {goal}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔥 *Калории:* {cal} / {DAILY_NORM['calories']} ккал\n"
        f"{progress_bar(cal, DAILY_NORM['calories'])}\n\n"
        f"🥩 *Белки:* {prot} / {DAILY_NORM['protein']} г\n"
        f"{progress_bar(prot, DAILY_NORM['protein'])}\n\n"
        f"🧈 *Жиры:* {fat} / {DAILY_NORM['fat']} г\n"
        f"{progress_bar(fat, DAILY_NORM['fat'])}\n\n"
        f"🍞 *Углеводы:* {carbs} / {DAILY_NORM['carbs']} г\n"
        f"{progress_bar(carbs, DAILY_NORM['carbs'])}\n\n"
        f"💧 *Вода:* {water} / {DAILY_NORM['water']} мл\n"
        f"{progress_bar(water, DAILY_NORM['water'])}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )


@dp.message(F.text == "💧 Вода")
async def water_menu(message: Message):
    user = get_stats(message.from_user.id)
    water = int(user[7]) if user and user[7] else 0
    await message.answer(
        f"💧 *Трекер воды*\n\n"
        f"Выпито сегодня: *{water} мл* из {DAILY_NORM['water']} мл\n"
        f"{progress_bar(water, DAILY_NORM['water'])}\n\n"
        f"Сколько добавить?",
        parse_mode="Markdown",
        reply_markup=water_keyboard()
    )


@dp.callback_query(F.data.startswith("water_"))
async def add_water_handler(callback: CallbackQuery):
    ml = int(callback.data.split("_")[1])
    add_water(callback.from_user.id, ml)
    user = get_stats(callback.from_user.id)
    water = int(user[7]) if user and user[7] else ml
    await callback.message.edit_text(
        f"💧 Добавлено *{ml} мл*!\n\n"
        f"Выпито сегодня: *{water} мл* из {DAILY_NORM['water']} мл\n"
        f"{progress_bar(water, DAILY_NORM['water'])}",
        parse_mode="Markdown"
    )


@dp.message(F.text == "⚖️ Мой вес")
async def weight_menu(message: Message):
    user = get_stats(message.from_user.id)
    current = user[9] if user and user[9] else None
    history = get_weight_history(message.from_user.id)

    text = f"⚖️ *Трекер веса*\n\n"
    if current:
        text += f"Текущий вес: *{current} кг*\n\n"
    if history:
        text += "*История (последние 7 записей):*\n"
        for weight, d in history:
            text += f"• {d}: {weight} кг\n"
    text += "\n📝 Отправь свой вес числом, например: `75.5`"

    await message.answer(text, parse_mode="Markdown")


@dp.message(F.text.regexp(r"^\d+([.,]\d+)?$"))
async def save_weight(message: Message):
    weight = float(message.text.replace(",", "."))
    if 30 <= weight <= 300:
        add_weight(message.from_user.id, weight)
        await message.answer(
            f"⚖️ Вес *{weight} кг* сохранён!\n\n"
            f"Продолжай в том же духе 💪",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Введи корректный вес (от 30 до 300 кг)")


@dp.message(F.text == "💪 Тренировка")
async def workout(message: Message):
    user = get_stats(message.from_user.id)
    goal = user[2] if user else "поддержание формы"
    await message.answer("⏳ Генерирую тренировку под твою цель...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Составь программу тренировки на сегодня. "
                 f"Цель пользователя: {goal}. "
                 f"Формат: эмодзи + название упражнения, подходы x повторения, отдых. "
                 f"5-7 упражнений. Компактно и мотивирующе. Добавь мотивационную фразу в конце."
    )
    await message.answer(
        f"💪 *Тренировка на сегодня:*\n\n{response.text}",
        parse_mode="Markdown",
        reply_markup=workout_keyboard()
    )


@dp.callback_query(F.data == "workout_done")
async def workout_done(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏆 *Отличная работа!* Тренировка выполнена!\n\n"
        "💪 Ты на шаг ближе к своей цели!\n"
        "🍽 Не забудь про питание и воду!",
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "workout_new")
async def workout_new(callback: CallbackQuery):
    user = get_stats(callback.from_user.id)
    goal = user[2] if user else "поддержание формы"
    await callback.message.edit_text("⏳ Генерирую новую тренировку...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Составь ДРУГУЮ программу тренировки. "
                 f"Цель: {goal}. Другие упражнения чем обычно. "
                 f"Формат: эмодзи + название, подходы x повторения, отдых. 5-7 упражнений."
    )
    await callback.message.edit_text(
        f"💪 *Альтернативная тренировка:*\n\n{response.text}",
        parse_mode="Markdown",
        reply_markup=workout_keyboard()
    )


@dp.message(F.text == "📸 Анализ еды")
async def ask_photo(message: Message):
    await message.answer("📸 Отправь фото своей еды — определю КБЖУ мгновенно!")


@dp.message(F.photo)
async def analyze_food(message: Message):
    await message.answer("⏳ Анализирую...")
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=file_bytes.read(), mime_type="image/jpeg"),
            "Ты нутрициолог. Определи блюдо на фото и дай КБЖУ на порцию. "
            "Формат строго:\nБлюдо: название\nКалории: X ккал\nБелки: X г\nЖиры: X г\nУглеводы: X г\n"
            "Только цифры без диапазонов. Коротко."
        ]
    )

    text = response.text
    await message.answer(
        f"🍽 *Результат анализа:*\n\n{text}\n\n"
        f"_Данные добавлены в дневник_ ✅",
        parse_mode="Markdown"
    )

    try:
        lines = text.split('\n')
        cal = prot = fat = carbs = 0
        for line in lines:
            if 'Калории' in line:
                cal = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif 'Белки' in line:
                prot = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif 'Жиры' in line:
                fat = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif 'Углеводы' in line:
                carbs = int(''.join(filter(str.isdigit, line.split(':')[1])))
        add_calories(message.from_user.id, cal, prot, fat, carbs)
    except:
        pass


@dp.message(F.text)
async def chat(message: Message):
    await message.answer("⏳ Думаю...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Ты AI фитнес-тренер и нутрициолог. "
                 f"Отвечай коротко, по делу, с эмодзи. "
                 f"Вопрос: {message.text}"
    )
    await message.answer(response.text)


async def main():
    init_db()
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())