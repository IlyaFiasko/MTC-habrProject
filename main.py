from db_utils import (
    get_article_by_url,
    insert_article,
    get_article_id,
    delete_comments_for_article,
    insert_comments,
    needs_comment_update
)
from articles_parser import fetch_html, parse_article
from comments_parser import fetch_comments
from classifier import classify_comments
from summarizer import summarize

def process_article(url: str) -> dict:
    article_row = get_article_by_url(url)

    if article_row is None:
        html = fetch_html(url)
        parsed = parse_article(html)

        if not parsed or not parsed.get("content"):
            print("[ОШИБКА] Парсер не смог получить содержимое статьи.")
            return None

        title, content = parsed['title'], parsed['content']
        summary = summarize(content)
        insert_article(url, title, content, summary)
        article_id = get_article_id(url)
        is_new = True
    else:
        article_id = article_row[0]
        summary = article_row[4]
        is_new = False

        if not needs_comment_update(article_row):
            return {
                "is_new": is_new,
                "summary": summary,
                "article_id": article_id
            }

        delete_comments_for_article(article_id)

    comments = fetch_comments(url)
    comments_with_sentiment = classify_comments(comments)
    insert_comments(article_id, comments_with_sentiment)

    return {
        "is_new": is_new,
        "summary": summary,
        "article_id": article_id
    }