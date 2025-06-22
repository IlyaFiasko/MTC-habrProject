import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from main import process_article
from db_utils import get_comments_by_sentiment

API_TOKEN = '7509427258:AAEiO2Vjc_uAd44fwFh6WlI-xpyQY0b7ay8'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📄 Посмотреть выжимку статьи", callback_data="summary"),
        InlineKeyboardButton("💬 Комментарии", callback_data="comments")
    )
    return keyboard

def comments_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("👍 Позитивные", callback_data="positive"),
        InlineKeyboardButton("😐 Нейтральные", callback_data="neutral"),
        InlineKeyboardButton("👎 Негативные", callback_data="negative"),
        InlineKeyboardButton("↩️ Назад", callback_data="back_main")
    )
    return keyboard

def back_to_comments():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("↩️ Назад к выбору комментариев", callback_data="comments"))
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("👋 Отправь ссылку на статью с Habr, чтобы я её обработал.")

@dp.message_handler(lambda msg: msg.text.startswith("https://habr.com"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    await message.answer("🔄 Обрабатываем статью, подожди немного...")

    result = process_article(url)

    if result["is_new"]:
        await message.answer("✅ Новая статья сохранена!")
    else:
        await message.answer("ℹ️ Статья уже была в базе.")

    # Сохраняем состояние
    user_states[message.from_user.id] = {
        "summary": result["summary"],
        "article_id": result["article_id"]
    }

    await message.answer("Что хочешь посмотреть?", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data in ["summary", "comments", "positive", "neutral", "negative", "back_main"])
async def handle_buttons(callback_query: types.CallbackQuery):
    action = callback_query.data
    user_id = callback_query.from_user.id

    if user_id not in user_states:
        await bot.send_message(user_id, "❗ Сначала пришли ссылку на статью.")
        return

    article_id = user_states[user_id]["article_id"]

    if action == "summary":
        summary = user_states[user_id]["summary"]
        MAX_LENGTH = 4096
        parts = [summary[i:i + MAX_LENGTH] for i in range(0, len(summary), MAX_LENGTH)]

        for part in parts[:-1]:
            await bot.send_message(user_id, part)

        await bot.send_message(user_id, parts[-1], reply_markup=main_menu())

    elif action == "comments":
        await bot.send_message(user_id, "Выбери тип комментариев:", reply_markup=comments_menu())

    elif action in ["positive", "neutral", "negative"]:
        comments = get_comments_by_sentiment(article_id, action)
        if not comments:
            await bot.send_message(user_id, "😔 Нет комментариев этого типа.")
            return
    
        text = f"💬 {action.capitalize()} комментарии:\n\n" + "\n\n".join(comments)
        MAX_LENGTH = 4096
        parts = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
    
        for part in parts[:-1]:
            await bot.send_message(user_id, part)
    
        await bot.send_message(user_id, parts[-1], reply_markup=back_to_comments())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
