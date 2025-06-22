from transformers import pipeline

clf = pipeline("text-classification", model="blanchefort/rubert-base-cased-sentiment-rusentiment")

def classify_comment(text: str) -> str:
    try:
        print(f"[КЛАССИФИКАТОР] Классифицируем: {text[:60]}...")
        result = clf(text)[0]
        label = result["label"].lower()
        print(f"[КЛАССИФИКАТОР] Результат: {label}")
        return label
    except Exception as e:
        print(f"[КЛАССИФИКАТОР] Ошибка: {e}")
        return "neutral"

def classify_comments(comments: list[str]) -> list[tuple[str, str]]:
    print(f"[КЛАССИФИКАТОР] Начинаем классификацию {len(comments)} комментариев...")
    classified = [(c, classify_comment(c)) for c in comments]
    print("[КЛАССИФИКАТОР] Классификация завершена.")
    return classified
