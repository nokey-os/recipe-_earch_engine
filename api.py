import re
import requests
from config import RECIPE_API_URL


def _extract_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        meas = meal.get(f"strMeasure{i}")
        if ing and ing.strip():
            ingredients.append(f"{meas} {ing}".strip())
    return ingredients


def _parse_meal(meal):
    return {
        "id": meal["idMeal"],
        "title": meal["strMeal"],
        "image": meal["strMealThumb"],
        "instructions": meal["strInstructions"],
        "ingredients": _extract_ingredients(meal),
        "category": meal.get("strCategory", ""),
        "area": meal.get("strArea", ""),
        "video": meal.get("strYoutube", "") or "",
    }


def has_cyrillic(text):
    return bool(re.search(r"[а-яА-ЯёЁ]", text))


def search_by_name(query):
    url = f"{RECIPE_API_URL}/search.php"
    try:
        resp = requests.get(url, params={"s": query}, timeout=10)
        data = resp.json()
        return [_parse_meal(m) for m in (data.get("meals") or [])]
    except Exception as e:
        print(f"search_by_name error: {e}")
        return []


def search_by_ingredient(query):
    url = f"{RECIPE_API_URL}/filter.php"
    try:
        resp = requests.get(url, params={"i": query}, timeout=10)
        data = resp.json()
        meals = data.get("meals") or []
        results = []
        for m in meals[:5]:
            detail = get_recipe_by_id(m["idMeal"])
            if detail:
                results.append(detail)
        return results
    except Exception as e:
        print(f"search_by_ingredient error: {e}")
        return []


def search_recipe(query):
    if has_cyrillic(query):
        return []

    results = search_by_name(query)
    if not results:
        results = search_by_ingredient(query)
    return results


def get_recipe_by_id(recipe_id):
    url = f"{RECIPE_API_URL}/lookup.php"
    try:
        resp = requests.get(url, params={"i": recipe_id}, timeout=10)
        data = resp.json()
        meal = (data.get("meals") or [None])[0]
        return _parse_meal(meal) if meal else None
    except Exception as e:
        print(f"get_recipe_by_id error: {e}")
        return None


def recipe_to_text(recipe):
    text = f"<b>{recipe['title']}</b>\n"
    if recipe.get("rating"):
        text += f"⭐️ <b>Рейтинг:</b> {recipe['rating']}/5\n"
    if recipe.get("category"):
        text += f"📂 <b>Категория:</b> {recipe['category']}\n"
    if recipe.get("area"):
        text += f"🌍 <b>Кухня:</b> {recipe['area']}\n"
    if recipe.get("video"):
        text += f'🎥 <a href="{recipe["video"]}">Видеорецепт на YouTube</a>\n'
    text += "\n<b>Ингредиенты:</b>\n"
    for ing in recipe["ingredients"]:
        text += f"• {ing}\n"
    instr = (recipe.get("instructions") or "")[:500]
    text += f"\n<b>Инструкция:</b>\n{instr}..."
    return text
