import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

app_flask = Flask(__name__)
telegram_app = None

async def setup_bot():
    global telegram_app
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    
    telegram_app.add_handler(CommandHandler("reply", reply_to_user))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
    await telegram_app.initialize()

# User Message Handler
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

# Admin Reply Handler
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

@app_flask.route('/')
def home():
    return "Bot is alive and running!"

@app_flask.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    import asyncio
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, telegram_app.bot)
    
    # Run async update inside Flask
    asyncio.run(telegram_app.process_update(update))
    return "OK", 200

if __name__ == '__main__':
    import asyncio
    asyncio.run(setup_bot())
    
    # Set Webhook automatically when starting on cloud (Optional or can set manually)
    PORT = int(os.environ.get('PORT', 5000))
    app_flask.run(host='0.0.0.0', port=PORT)
  
