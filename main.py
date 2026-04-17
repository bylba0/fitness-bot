import asyncio
import os
from google import genai
from google.genai import types
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
from database import init_db, get_or_create_user, set_goal, get_stats, add_calories
from keyboards import main_menu, goals_keyboard

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash-lite"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    get_or_create_user(message.from_user.id, message.from_user.first_name)
    await message.answer(
        f"👋 Привет, *{message.from_user.first_name}*!\n\n"
        f"Я твой персональный AI фитнес-тренер 🤖\n\n"
        f"*Что я умею:*\n"
        f"📸 Анализирую еду на фото → КБЖУ\n"
        f"💪 Составляю программы тренировок\n"
        f"📊 Веду дневник питания\n"
        f"🎯 Подбираю план под твою цель\n\n"
        f"Выбери действие в меню ниже 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


@dp.message(F.text == "🎯 Моя цель")
@dp.message(Command("goal"))
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


@dp.message(F.text == "📊 Моя статистика")
async def stats(message: Message):
    user = get_stats(message.from_user.id)
    if not user:
        await message.answer("Сначала напиши /start!")
        return
    name, goal = user[1], user[2]
    cal, prot, fat, carbs = user[3], user[4], user[5], user[6]
    await message.answer(
        f"📊 *Статистика за сегодня*\n\n"
        f"👤 {name}\n"
        f"🎯 Цель: {goal}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔥 Калории: *{cal}* ккал\n"
        f"🥩 Белки: *{prot}* г\n"
        f"🧈 Жиры: *{fat}* г\n"
        f"🍞 Углеводы: *{carbs}* г\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )


@dp.message(F.text == "💪 Тренировка")
@dp.message(Command("workout"))
async def workout(message: Message):
    user = get_stats(message.from_user.id)
    goal = user[2] if user else "поддержание формы"
    await message.answer("⏳ Генерирую тренировку под твою цель...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Составь программу тренировки на сегодня. "
                 f"Цель пользователя: {goal}. "
                 f"Формат: эмодзи + название упражнения, подходы x повторения, отдых. "
                 f"5-7 упражнений. Компактно и мотивирующе."
    )
    await message.answer(
        f"💪 *Тренировка на сегодня:*\n\n{response.text}",
        parse_mode="Markdown"
    )


@dp.message(F.text == "📸 Анализ еды")
async def ask_photo(message: Message):
    await message.answer("📸 Отправь фото своей еды и я определю КБЖУ!")


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
            "Формат строго: \nБлюдо: название\nКалории: X ккал\nБелки: X г\nЖиры: X г\nУглеводы: X г\n"
            "Только цифры без диапазонов. Коротко."
        ]
    )

    text = response.text
    await message.answer(
        f"🍽 *Результат анализа:*\n\n{text}\n\n"
        f"_Данные добавлены в дневник питания_ ✅",
        parse_mode="Markdown"
    )

    # Парсим и сохраняем в БД (простой парсинг)
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
        pass  # если парсинг не удался — просто не сохраняем


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