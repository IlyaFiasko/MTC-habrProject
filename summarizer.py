from transformers import AutoTokenizer, T5ForConditionalGeneration

print("[СУММАРИЗАТОР] Загружаем модель и токенизатор...")
model_name = "IlyaGusev/rut5_base_sum_gazeta"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
print("[СУММАРИЗАТОР] Модель загружена успешно.")

def summarize(text: str) -> str:
    print(f"[СУММАРИЗАТОР] Начинаем суммаризацию текста. Длина текста: {len(text)} символов.")

    try:
        input_ids = tokenizer(
            [text],
            max_length=600,
            add_special_tokens=True,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )["input_ids"]

        output_ids = model.generate(
            input_ids=input_ids,
            no_repeat_ngram_size=4
        )[0]

        summary = tokenizer.decode(output_ids, skip_special_tokens=True)
        print(f"[СУММАРИЗАТОР] Суммаризация завершена. Длина выжимки: {len(summary)} символов.")
        return summary

    except Exception as e:
        print("[СУММАРИЗАТОР] Ошибка при суммаризации текста:", str(e))
        return "[Ошибка при суммаризации]"