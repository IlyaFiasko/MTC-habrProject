import sqlite3
from datetime import datetime, timedelta

DB_PATH = "articles.db"

def get_article_by_url(url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result

def insert_article(url, title, content, summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO articles (url, title, content, summary, date_parsed)
        VALUES (?, ?, ?, ?, ?)
    """, (url, title, content, summary, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def delete_comments_for_article(article_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments WHERE article_id = ?", (article_id,))
    conn.commit()
    conn.close()

def insert_comments(article_id, comments_with_sentiment):
    print(f"[БД] Добавляем {len(comments_with_sentiment)} комментариев в базу для article_id={article_id}")
    conn = sqlite3.connect("articles.db")
    cur = conn.cursor()

    date_parsed = datetime.now().isoformat()

    for comment, sentiment in comments_with_sentiment:
        print(f"[БД] Вставка: {sentiment} — {comment[:60]}...")
        cur.execute("""
            INSERT INTO comments (article_id, content, sentiment, date_parsed)
            VALUES (?, ?, ?, ?)
        """, (article_id, comment, sentiment, date_parsed))

    conn.commit()
    conn.close()
    print("[БД] Вставка завершена.")

def needs_comment_update(article_row, days_threshold=3):
    date_parsed = datetime.fromisoformat(article_row[5])
    return datetime.now() - date_parsed > timedelta(days=days_threshold)

def get_article_id(url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_comments_summary(article_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sentiment, COUNT(*) FROM comments
        WHERE article_id = ?
        GROUP BY sentiment
    """, (article_id,))
    result = cursor.fetchall()
    conn.close()
    summary = {"positive": 0, "neutral": 0, "negative": 0}
    for sentiment, count in result:
        summary[sentiment] = count
    return summary

def get_comments_by_sentiment(article_id: int, sentiment: str):
    conn = sqlite3.connect("articles.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT content FROM comments
        WHERE article_id = ? AND sentiment = ?
        LIMIT 10
    """, (article_id, sentiment))
    results = cur.fetchall()
    conn.close()
    return [r[0] for r in results]

def update_article_summary(article_id: int, new_summary: str):
    conn = sqlite3.connect("articles.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE articles SET summary = ? WHERE id = ?
    """, (new_summary, article_id))
    conn.commit()
    conn.close()