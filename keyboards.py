from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🔍 Поиск рецептов")],
            [KeyboardButton("📋 Мои рецепты")],
        ],
        resize_keyboard=True,
    )


def recipes_list_keyboard(recipes):
    buttons = []
    for r in recipes:
        stars = "⭐" * r.get("rating", 0)
        title = f"{stars} {r['title']}" if stars else r['title']
        buttons.append([InlineKeyboardButton(title, callback_data=f"view_{r['id']}")])
    return InlineKeyboardMarkup(buttons)


def search_results_keyboard(results):
    buttons = []
    for r in results:
        buttons.append([InlineKeyboardButton(r["title"], callback_data=f"detail_{r['id']}")])
    return InlineKeyboardMarkup(buttons)


def recipe_actions_keyboard(recipe_id, saved=False):
    if saved:
        buttons = [
            [InlineKeyboardButton("❌ Удалить из избранного", callback_data=f"del_{recipe_id}")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton("❤️ Сохранить в избранное", callback_data=f"save_{recipe_id}")],
        ]
    return InlineKeyboardMarkup(buttons)


def saved_recipe_detail_keyboard(recipe_id, rating=0):
    buttons = []
    rating_row = []
    for i in range(1, 6):
        star = "⭐" if i <= rating else "☆"
        rating_row.append(InlineKeyboardButton(star, callback_data=f"rate_{recipe_id}_{i}"))
    buttons.append(rating_row)
    buttons.append([InlineKeyboardButton("❌ Удалить из избранного", callback_data=f"del_{recipe_id}")])
    return InlineKeyboardMarkup(buttons)
