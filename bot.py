from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = 'ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН'

# Вопросы и этапы
questions = [
    {"key": "budget", "text": "1️⃣ Какой бюджет?", "options": [("< 50k", 1), ("50k–100k", 2), ("> 100k", 3)]},
    {"key": "relationship", "text": "2️⃣ Как отношения с клиентом?", "options": [("Холодные", 0), ("Нейтральные", 1), ("Тёплые", 2)]},
    {"key": "lpr", "text": "3️⃣ Знакомы с ЛПР или CEO?", "options": [("Нет", 0), ("Да", 1)]},
    {"key": "partnership", "text": "4️⃣ Готовы к постоянному сотрудничеству?", "options": [("Нет", 0), ("Возможно", 1), ("Да", 2)]},
    {"key": "strategy", "text": "5️⃣ Стратегическая важность клиента?", "options": [("Низкая", 0), ("Средняя", 1), ("Высокая", 2)]},
    {"key": "tech", "text": "6️⃣ Планируются технологии или интерактивы?", "options": [("Нет", 0), ("Да", 1)]},
]

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {"step": 0, "answers": {}}
    keyboard = [[KeyboardButton("🚀 Начать")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Этот бот поможет оценить, стоит ли участвовать в тендере. Просто нажми кнопку ниже:",
        reply_markup=reply_markup
    )

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"step": 0, "answers": {}}
    await send_question(update, context, user_id)

async def send_question(update_or_query, context, user_id):
    step = user_sessions[user_id]["step"]
    if step < len(questions):
        q = questions[step]
        buttons = [[InlineKeyboardButton(txt, callback_data=f"{q['key']}|{score}")] for txt, score in q["options"]]
        if step > 0:
            buttons.append([InlineKeyboardButton("◀ Назад", callback_data="back")])
        if getattr(update_or_query, 'callback_query', None):
            await update_or_query.callback_query.edit_message_text(q["text"], reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update_or_query.message.reply_text(q["text"], reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await show_result(update_or_query, user_id)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_sessions:
        user_sessions[user_id] = {"step": 0, "answers": {}}

    step = user_sessions[user_id]["step"]

    if query.data == "back":
        if step > 0:
            user_sessions[user_id]["step"] -= 1
        await send_question(update, context, user_id)
        return

    key, score = query.data.split("|")
    user_sessions[user_id]["answers"][key] = int(score)
    user_sessions[user_id]["step"] += 1
    await send_question(update, context, user_id)

async def show_result(update, user_id):
    total = sum(user_sessions[user_id]["answers"].values())
    if total >= 8:
        result = "✅ Рекомендуется участвовать!"
    elif total >= 5:
        result = "🟡 Под вопросом. Нужно уточнить детали."
    else:
        result = "❌ Не участвовать."

    await update.callback_query.edit_message_text(f"Итоговая оценка: {total}/11\n{result}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🚀 Начать"), handle_start_button))
    app.add_handler(CallbackQueryHandler(handle_answer))
    print("Бот запущен. Напиши /start или нажми кнопку")
    app.run_polling()
