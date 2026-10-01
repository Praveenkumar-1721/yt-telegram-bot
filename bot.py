import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

app_flask = Flask(__name__)

# Initialize Telegram Application globally
telegram_app = ApplicationBuilder().token(TOKEN).build()

# 1. First, define the User Message Handler function
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text
    if user.id == ADMIN_CHAT_ID:
        return

    admin_text = (
        f"📩 New Message from YouTube User!\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🔗 Username: @{user.username if user.username else 'None'}\n"
        f"🆔 User ID: `{user.id}`\n\n"
        f"💬 Message:\n{user_message}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="Markdown")
    await update.message.reply_text("Vanakkam! Ungaloda message nalla vanthu sernthuruchu. Seekiram ungalukku reply panrom.")

# 2. Next, define the Admin Reply Handler function
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Unakku antha permission illa da!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage format: `/reply <User_ID> <Your Message>`", parse_mode="Markdown")
        return

    target_user_id = context.args[0]
    reply_message = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=target_user_id, text=f"📢 Message from Admin/Creator:\n\n{reply_message}")
        await update.message.reply_text("✅ Reply sent successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# 3. Now, setup the handlers (since functions are already defined above)
async def setup_handlers():
    telegram_app.add_handler(CommandHandler("reply", reply_to_user))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
    await telegram_app.initialize()

# Run setup during startup
asyncio.run(setup_handlers())

@app_flask.route('/')
def home():
    return "Bot is alive and running!"

@app_flask.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, telegram_app.bot)
    
    asyncio.run(telegram_app.process_update(update))
    return "OK", 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app_flask.run(host='0.0.0.0', port=PORT)
