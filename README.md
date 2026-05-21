# 🍳 Recipe Bot — Telegram бот для поиска рецептов

<img width="866" height="872" alt="image" src="https://github.com/user-attachments/assets/945c706f-d38f-41ef-80ed-ae90ee799fbf" />

<img width="918" height="841" alt="image" src="https://github.com/user-attachments/assets/1dee5285-e60b-4e35-8446-8db24521cd87" />


Telegram-бот для поиска рецептов через [TheMealDB API](https://www.themealdb.com/). Позволяет искать блюда, сохранять их в избранное, оценивать по шкале от 1 до 5 ⭐ и смотреть видеорецепты.

## Возможности

- 🔍 **Поиск рецептов** — по названию или ингредиенту (английский язык)
- 📋 **Избранное** — список сохранённых рецептов, отсортированных по рейтингу
- ⭐ **Рейтинг** — оценка рецептов от 1 до 5 звёзд
- 🎥 **Видеорецепты** — ссылка на YouTube, если доступна
- 💾 **Сохранение в SQLite** — рецепты хранятся локально

## Структура проекта

```
├── main.py           # Точка входа, хендлеры команд и колбэков
├── api.py            # Взаимодействие с TheMealDB API
├── database.py       # Работа с SQLite (сохранение, удаление, рейтинг)
├── keyboards.py      # Клавиатуры и кнопки
├── config.py         # Конфигурация (токен, URL API) — НЕ КОММИТИТЬ
├── requirements.txt  # Зависимости
└── README.md
```

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/nokey-os/recipe-_earch_engine.git
cd recipe-_earch_engine

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать config.py с токеном бота
echo 'BOT_TOKEN = "ваш_токен_от_BotFather"' > config.py
echo 'RECIPE_API_URL = "https://www.themealdb.com/api/json/v1/1"' >> config.py
echo 'DATABASE_PATH = "recipes.db"' >> config.py

# 4. Запустить
python main.py
```

## Как получить токен

1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен в `config.py`

## Использование

| Команда / Кнопка         | Описание                              |
|--------------------------|---------------------------------------|
| `/start`                 | Запуск бота, показ главного меню      |
| 🔍 **Поиск рецептов**    | Ввод названия блюда на английском     |
| 📋 **Мои рецепты**       | Список сохранённых рецептов           |
| ❤️ Сохранить             | Добавить рецепт в избранное           |
| ❌ Удалить               | Удалить рецепт из избранного          |
| ⭐ (1–5)                 | Оценить рецепт                        |

> Поиск работает только на **английском языке** (TheMealDB API не поддерживает кириллицу). Например: `chicken`, `pasta`, `tomato`, `rice`.

## Технологии

- Python 3.12
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21+
- SQLite
- TheMealDB API (бесплатный)
