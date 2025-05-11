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

from transformers import AutoModelForCausalLM, LlamaTokenizer, AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Суммаризация текста (YandexGPT)
MODEL_NAME_SUM = "yandex/YandexGPT-5-Lite-8B-instruct"
tokenizer_sum = LlamaTokenizer(vocab_file="/tokenizer.model")
model_sum = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME_SUM,
    device_map="cuda",
    torch_dtype="auto",
    trust_remote_code=True
)

def generate_summary(text: str) -> str:
    prompt = f"<s>[INST] Кратко перескажи статью: {text} [/INST]"
    input_ids = tokenizer_sum(prompt, return_tensors="pt").input_ids.to("cuda")
    outputs = model_sum.generate(input_ids, max_new_tokens=512)
    return tokenizer_sum.decode(outputs[0][input_ids.shape[1]:], skip_special_tokens=True)

# Классификация комментариев (RuBERT)
MODEL_NAME_CLASS = "blanchefort/rubert-base-cased-sentiment"
tokenizer_cls = AutoTokenizer.from_pretrained(MODEL_NAME_CLASS)
model_cls = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME_CLASS)

labels_map = {0: "negative", 1: "neutral", 2: "positive"}

def classify_comment(text: str) -> str:
    inputs = tokenizer_cls(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model_cls(**inputs)
    probs = F.softmax(outputs.logits, dim=1)
    predicted_class = torch.argmax(probs, dim=1).item()
    return labels_map[predicted_class]


def main(url: str):
    # Проверяем, есть ли статья
    article_row = get_article_by_url(url)

    if article_row is None:
        print("Парсим новую статью...")
        html = fetch_html(url)
        parsed = parse_article(html)
        title, content = parsed['title'], parsed['text']
        summary = generate_summary(content)
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
    comments_with_sentiment = [(c, classify_comment(c)) for c in comments]
    insert_comments(article_id, comments_with_sentiment)
    print(f"Сохранено комментариев: {len(comments)}")

if __name__ == "__main__":
    url = ''
    main(url)
