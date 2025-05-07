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

def main(url: str):
    # Проверяем, есть ли статья
    article_row = get_article_by_url(url)

    if article_row is None:
        print("Парсим новую статью...")
        html = fetch_html(url)
        parsed = parse_article(html)
        title, content = parsed['title'], parsed['text']
        summary = content[:200]  # можно использовать генератор резюме позже
        insert_article(url, title, content, summary)
        article_id = get_article_id(url)
    else:
        print("Статья уже есть в базе.")
        article_id = article_row[0]
        if not needs_comment_update(article_row):
            print("Комментарии не требуют обновления.")
            return
        print("Обновляем комментарии...")
        delete_comments_for_article(article_id)

    # Загружаем и записываем комментарии
    comments = fetch_comments(url)
    comments_with_sentiment = [(c, 'neutral') for c in comments]
    insert_comments(article_id, comments_with_sentiment)
    print(f"Сохранено комментариев: {len(comments)}")

if __name__ == "__main__":
    urls = ['https://habr.com/ru/companies/ru_mts/articles/906114/', 'https://habr.com/ru/companies/ru_mts/articles/906884/', 'https://habr.com/ru/companies/ru_mts/articles/905614/', 'https://habr.com/ru/companies/ru_mts/articles/904330/', 'https://habr.com/ru/companies/ru_mts/articles/904016/', 'https://habr.com/ru/companies/oleg-bunin/articles/902932/', 'https://habr.com/ru/companies/ru_mts/articles/903142/', 'https://habr.com/ru/companies/ru_mts/articles/902806/', 'https://habr.com/ru/companies/ru_mts/articles/902244/', 'https://habr.com/ru/companies/ru_mts/articles/902106/', 'https://habr.com/ru/companies/ru_mts/articles/901992/', 'https://habr.com/ru/companies/ru_mts/articles/901266/', 'https://habr.com/ru/companies/ru_mts/articles/900596/', 'https://habr.com/ru/companies/ru_mts/articles/900288/', 'https://habr.com/ru/companies/ru_mts/articles/899964/', 'https://habr.com/ru/companies/ru_mts/articles/899904/']
    for url in urls:
        main(url)