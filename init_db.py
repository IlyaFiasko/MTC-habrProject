import sqlite3

def init_db():
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    # Создание таблицы статей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        summary TEXT NOT NULL,
        date_parsed TIMESTAMP NOT NULL
    )
    """)

    # Создание таблицы комментариев
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        article_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative')) NOT NULL,
        date_parsed TIMESTAMP NOT NULL,
        FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
    print("База данных успешно создана.")

if __name__ == "__main__":
    init_db()