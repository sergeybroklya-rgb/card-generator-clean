import os
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""

import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== ТВОИ ДАННЫЕ ====================
BOT_TOKEN = ""  # Токен от @SmartCard1_Bot
CHANNEL_ID = -1003974476267  # ЗАМЕНИ НА СВОЙ ID КАНАЛА (отрицательное число)

# ==================== БАЗА ДАННЫХ ====================
conn = sqlite3.connect('payments.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        created_at TEXT
    )
''')
conn.commit()

def save_payment(email: str) -> int:
    cursor.execute("INSERT INTO payments (email, created_at) VALUES (?, ?)",
                   (email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    return cursor.lastrowid

# ==================== УВЕДОМЛЕНИЕ В КАНАЛ ====================
async def send_notification(payment_id: int, email: str):
    """Отправляет уведомление в канал (клиент это не видит)"""
    text = f"🆕 НОВАЯ ЗАЯВКА #{payment_id}\n📧 {email}"
    try:
        await application.bot.send_message(chat_id=CHANNEL_ID, text=text)
        print(f"✅ Уведомление отправлено в канал (заявка #{payment_id})")
    except Exception as e:
        print(f"❌ Ошибка отправки в канал: {e}")

# ==================== КОМАНДЫ БОТА ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Купить подписку", callback_data="buy")]
    ])
    await update.message.reply_text(
        "🤖 *Подписка 3000 ₽/мес*\n\n"
        "Нажмите кнопку ниже, чтобы оформить подписку на генератор карточек товаров.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✏️ *Введите ваш email*, который вы использовали при регистрации в сервисе.\n\n"
        "Пример: `user@example.com`",
        parse_mode="Markdown"
    )
    context.user_data['awaiting_email'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_email'):
        email = update.message.text.strip()
        context.user_data['awaiting_email'] = False
        
        # Простая проверка email
        if '@' not in email or '.' not in email:
            await update.message.reply_text("❌ Неверный формат email. Попробуйте ещё раз.")
            return
        
        payment_id = save_payment(email)
        
        # Отправляем уведомление В КАНАЛ
        await send_notification(payment_id, email)
        
        # Ответ клиенту
        await update.message.reply_text(
            f"✅ *Заявка #{payment_id} принята!*\n\n"
            f"📧 {email}\n\n"
            f"📩 Мы свяжемся с вами в течение 24 часов.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🤖 Нажмите /start для начала работы.",
            parse_mode="Markdown"
        )

# ==================== ЗАПУСК ====================
def main():
    global application
    print("🚀 Запуск бота для оплаты подписки...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен! Напишите /start в Telegram")
    application.run_polling()

if __name__ == "__main__":
    main()