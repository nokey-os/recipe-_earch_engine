import sqlite3
from config import DATABASE_PATH


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id TEXT NOT NULL,
            title TEXT NOT NULL,
            image TEXT,
            instructions TEXT,
            ingredients TEXT,
            video TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            UNIQUE(user_id, recipe_id)
        )
    """)
    for col in ["rating INTEGER DEFAULT 0", "video TEXT DEFAULT ''"]:
        try:
            cur.execute(f"ALTER TABLE saved_recipes ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def save_recipe(user_id, recipe_id, title, image, instructions, ingredients, video=""):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO saved_recipes
        (user_id, recipe_id, title, image, instructions, ingredients, video)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, recipe_id, title, image, instructions, ingredients, video))
    conn.commit()
    conn.close()


def delete_recipe(user_id, recipe_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM saved_recipes
        WHERE user_id = ? AND recipe_id = ?
    """, (user_id, recipe_id))
    conn.commit()
    conn.close()


def rate_recipe(user_id, recipe_id, rating):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE saved_recipes
        SET rating = ?
        WHERE user_id = ? AND recipe_id = ?
    """, (rating, user_id, recipe_id))
    conn.commit()
    conn.close()


def get_user_recipes(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT recipe_id, title, image, instructions, ingredients, video, rating
        FROM saved_recipes
        WHERE user_id = ?
        ORDER BY rating DESC, id DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [{
        "id": r[0], "title": r[1], "image": r[2],
        "instructions": r[3], "ingredients": r[4].split("\n"),
        "video": r[5], "rating": r[6],
    } for r in rows]


def get_saved_recipe(user_id, recipe_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT recipe_id, title, image, instructions, ingredients, video, rating
        FROM saved_recipes
        WHERE user_id = ? AND recipe_id = ?
    """, (user_id, recipe_id))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "title": row[1], "image": row[2],
        "instructions": row[3], "ingredients": row[4].split("\n"),
        "video": row[5], "rating": row[6],
    }


def is_saved(user_id, recipe_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM saved_recipes
        WHERE user_id = ? AND recipe_id = ?
    """, (user_id, recipe_id))
    exists = cur.fetchone() is not None
    conn.close()
    return exists
