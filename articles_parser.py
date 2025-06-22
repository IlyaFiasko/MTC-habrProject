import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_html(url: str) -> str:
    """Получение HTML-страницы по URL с Habr"""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

def parse_article(html: str) -> dict:
    """Парсит заголовок и текст статьи"""
    soup = BeautifulSoup(html, 'html.parser')
    
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else 'Заголовок не найден'
    
    body = soup.find('div', class_='tm-article-presenter__body')
    paragraphs = body.find_all(['p', 'h2', 'h3', 'blockquote']) if body else []
    content = '\n'.join(p.get_text(strip=True) for p in paragraphs)

    return {'title': title, 'content': content}