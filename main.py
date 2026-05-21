from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
from database import init_db, save_recipe, delete_recipe, rate_recipe, get_user_recipes, get_saved_recipe, is_saved
from api import search_recipe, get_recipe_by_id, recipe_to_text, has_cyrillic
from keyboards import start_keyboard, recipe_actions_keyboard, recipes_list_keyboard, search_results_keyboard, saved_recipe_detail_keyboard


async def start(update: Update, context):
    await update.message.reply_text(
        "🍳 <b>Добро пожаловать в бот рецептов!</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=start_keyboard(),
    )


async def handle_message(update: Update, context):
    text = update.message.text

    if text == "🔍 Поиск рецептов":
        await update.message.reply_text(
            "Введите название блюда или ингредиент для поиска:",
            reply_markup=start_keyboard(),
        )
        context.user_data["awaiting_search"] = True
        return

    if text == "📋 Мои рецепты":
        await show_my_recipes(update, context)
        return

    if context.user_data.get("awaiting_search"):
        context.user_data["awaiting_search"] = False
        query = text.strip()
        if not query:
            await update.message.reply_text(
                "Введите что-нибудь для поиска.",
                reply_markup=start_keyboard(),
            )
            return

        msg = await update.message.reply_text("🔎 Ищу рецепты...")
        results = search_recipe(query)

        if not results:
            if has_cyrillic(query):
                text = "🔤 <b>API рецептов поддерживает только английский язык.</b>\n\nПопробуйте ввести название блюда на английском:\nнапример: <i>chicken, pasta, tomato, rice</i>"
            else:
                text = "😕 Ничего не найдено. Попробуйте другой запрос."
            await msg.edit_text(text, parse_mode="HTML")
            await msg.reply_text(
                "Выберите действие:",
                reply_markup=start_keyboard(),
            )
            return

        try:
            await msg.delete()
        except Exception:
            pass
        context.user_data["last_search"] = results

        await update.message.reply_text(
            f"🔎 <b>Найдено рецептов:</b> {len(results)}\n\nНажмите на рецепт, чтобы посмотреть подробно:",
            parse_mode="HTML",
            reply_markup=search_results_keyboard(results[:10]),
        )

        if len(results) > 10:
            await update.message.reply_text(
                f"Показаны первые 10 из {len(results)}. Уточните запрос для большей точности.",
                reply_markup=start_keyboard(),
            )


async def show_my_recipes(update: Update, context):
    user_id = update.effective_user.id
    recipes = get_user_recipes(user_id)

    if not recipes:
        await update.message.reply_text(
            "📭 <b>У вас пока нет сохранённых рецептов.</b>\n\n"
            "Нажмите «🔍 Поиск рецептов», чтобы найти и сохранить их!",
            parse_mode="HTML",
            reply_markup=start_keyboard(),
        )
        return

    msg = await update.message.reply_text(
        f"📋 <b>Мои рецепты:</b> ({len(recipes)})\n\nНажмите на рецепт, чтобы посмотреть подробно:",
        parse_mode="HTML",
        reply_markup=recipes_list_keyboard(recipes),
    )
    context.user_data["recipe_list_msg"] = (msg.chat_id, msg.message_id)


async def callback_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("save_"):
        recipe_id = data.replace("save_", "")
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            await query.edit_message_text("Рецепт не найден.")
            return

        ingredients_str = "\n".join(recipe["ingredients"])
        save_recipe(
            user_id=user_id,
            recipe_id=recipe_id,
            title=recipe["title"],
            image=recipe["image"],
            instructions=recipe["instructions"],
            ingredients=ingredients_str,
            video=recipe.get("video", ""),
        )
        await query.edit_message_reply_markup(
            reply_markup=recipe_actions_keyboard(recipe_id, saved=True)
        )
        await query.message.reply_text("✅ Рецепт сохранён в избранное!")

    elif data.startswith("view_"):
        recipe_id = data.replace("view_", "")
        recipe = get_saved_recipe(user_id, recipe_id)
        if not recipe:
            await query.edit_message_text("Рецепт не найден.")
            return

        text = recipe_to_text(recipe)
        kb = saved_recipe_detail_keyboard(recipe_id, recipe.get("rating", 0))
        if recipe.get("image"):
            await query.message.reply_photo(
                photo=recipe["image"],
                caption=text[:1024],
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.message.reply_text(
                text=text,
                parse_mode="HTML",
                reply_markup=kb,
            )

    elif data.startswith("detail_"):
        recipe_id = data.replace("detail_", "")
        recipe = next((r for r in (context.user_data.get("last_search") or []) if r["id"] == recipe_id), None)
        if not recipe:
            recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            await query.edit_message_text("Рецепт не найден.")
            return

        text = recipe_to_text(recipe)
        kb = recipe_actions_keyboard(recipe_id, saved=is_saved(user_id, recipe_id))
        if recipe.get("image"):
            await query.message.reply_photo(
                photo=recipe["image"],
                caption=text[:1024],
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await query.message.reply_text(
                text=text,
                parse_mode="HTML",
                reply_markup=kb,
            )

    elif data.startswith("rate_"):
        parts = data.split("_")
        recipe_id = parts[1]
        rating = int(parts[2])
        rate_recipe(user_id, recipe_id, rating)
        recipe = get_saved_recipe(user_id, recipe_id)
        text = recipe_to_text(recipe)
        kb = saved_recipe_detail_keyboard(recipe_id, rating)
        try:
            await query.edit_message_caption(
                caption=text[:1024],
                parse_mode="HTML",
                reply_markup=kb,
            )
        except Exception:
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=kb,
            )

        list_msg = context.user_data.get("recipe_list_msg")
        if list_msg:
            chat_id, message_id = list_msg
            updated = get_user_recipes(user_id)
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"📋 <b>Мои рецепты:</b> ({len(updated)})\n\nНажмите на рецепт, чтобы посмотреть подробно:",
                    parse_mode="HTML",
                    reply_markup=recipes_list_keyboard(updated),
                )
            except Exception:
                pass

    elif data.startswith("del_"):
        recipe_id = data.replace("del_", "")
        delete_recipe(user_id, recipe_id)
        try:
            await query.edit_message_caption(
                caption="🗑 <b>Рецепт удалён из избранного</b>",
                parse_mode="HTML",
                reply_markup=None,
            )
        except Exception:
            await query.edit_message_text(
                text="🗑 <b>Рецепт удалён из избранного</b>",
                parse_mode="HTML",
                reply_markup=None,
            )

        list_msg = context.user_data.get("recipe_list_msg")
        if list_msg:
            chat_id, message_id = list_msg
            updated = get_user_recipes(user_id)
            if updated:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f"📋 <b>Мои рецепты:</b> ({len(updated)})\n\nНажмите на рецепт, чтобы посмотреть подробно:",
                        parse_mode="HTML",
                        reply_markup=recipes_list_keyboard(updated),
                    )
                except Exception:
                    pass
            else:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="📭 <b>Все рецепты удалены.</b>\n\nНажмите «🔍 Поиск рецептов», чтобы найти новые!",
                        parse_mode="HTML",
                        reply_markup=start_keyboard(),
                    )
                except Exception:
                    pass


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
