import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_comments(url: str) -> list:
    """
    Парсит комментарии со статьи Habr по URL.
    Автоматически переходит на страницу /comments/
    """
    if not url.endswith('/'):
        url += '/'
    comments_url = url + 'comments/'

    # Загружаем HTML
    response = requests.get(comments_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Парсинг блоков комментариев
    comment_blocks = soup.find_all('div', class_='tm-comment__body-content')
    comments = [block.get_text(strip=True) for block in comment_blocks]

    return comments