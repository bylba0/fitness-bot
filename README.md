# 🤖 FitneBot — AI Фитнес-тренер в Telegram

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green)](https://aiogram.dev)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange?logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

> Персональный AI фитнес-тренер в Telegram с анализом питания по фото и генерацией тренировок

---

## ✨ Возможности

| Функция | Описание |
|--------|----------|
| 📸 Анализ еды | Отправь фото — получи КБЖУ мгновенно |
| 💪 Тренировки | Программа под твою цель (масса/похудение/форма) |
| 📊 Дневник питания | Автоматический подсчёт КБЖУ за день |
| 🎯 Цели | Персонализация под задачу пользователя |
| 🤖 AI-чат | Вопросы по питанию и тренировкам |

---

## 🛠 Стек

- **Python 3.11**
- **aiogram 3.x** — Telegram Bot framework
- **Google Gemini 2.0** — AI модель (Vision + Text)
- **SQLite** — хранение данных пользователей
- **python-dotenv** — управление переменными окружения

---

## 🚀 Запуск

### 1. Клонируй репозиторий
```bash
git clone https://github.com/bylba0/fitness-bot.git
cd fitness-bot
```

### 2. Установи зависимости
```bash
pip install -r requirements.txt
```

### 3. Создай `.env` файл
```env
TELEGRAM_BOT_TOKEN=твой_токен
GEMINI_API_KEY=твой_ключ
```

### 4. Запусти
```bash
python main.py
```

---

## 📁 Структура проекта
fitness-bot

├── main.py          # Основной файл бота

├── database.py      # Работа с SQLite

├── keyboards.py     # Клавиатуры и кнопки

├── .env             # Переменные окружения (не публиковать!)

├── .gitignore       # Игнор файлов

├── requirements.txt # Зависимости

└── README.md        # Документация
---

## 📱 Демо

> Бот доступен в Telegram: [@Fitne22_bot](https://t.me/Fitne22_bot)

---

## 📄 Лицензия

MIT License — используй свободно с указанием автора.