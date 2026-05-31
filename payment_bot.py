import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

conn = sqlite3.connect("payments.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, created_at TEXT)")
conn.commit()

def save_payment(email):
    cursor.execute("INSERT INTO payments (email, created_at) VALUES (?, ?)", (email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    return cursor.lastrowid

async def start(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Купить подписку", callback_data="buy")]])
    await update.message.reply_text("🤖 *Подписка 3000 ₽/мес*\nНажми кнопку 👇", parse_mode="Markdown", reply_markup=keyboard)

async def button_callback(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✏️ Введите ваш email:")
    context.user_data["awaiting_email"] = True

async def handle_message(update, context):
    if context.user_data.get("awaiting_email"):
        email = update.message.text.strip()
        context.user_data["awaiting_email"] = False
        if "@" not in email or "." not in email:
            await update.message.reply_text("❌ Неверный email. Попробуйте ещё раз.")
            return
        payment_id = save_payment(email)
        await context.bot.send_message(chat_id=CHANNEL_ID, text=f"🆕 НОВАЯ ЗАЯВКА #{payment_id}\n📧 {email}")
        await update.message.reply_text(f"✅ *Заявка #{payment_id} принята!*\n\nМы свяжемся с вами в течение 24 часов.", parse_mode="Markdown")
    else:
        await update.message.reply_text("Нажмите /start для начала")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()