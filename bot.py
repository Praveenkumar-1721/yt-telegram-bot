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

# Start Command Handler (For both Admin & Users)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id == ADMIN_CHAT_ID:
        await update.message.reply_text(
            "👑 Vanakkam Boss!\n"
            "Cinematic Universe Support Bot active-ah irukku. "
            "Users send panra messages ellam ungalukku inge varum. Reply panraku `/reply <User_ID> <Message>` use pannunga! 🎬✨"
        )
    else:
        await update.message.reply_text(
            "🎬 Vanakkam Nanba!\n"
            "Cinematic Universe official support bot-ku ungalai anbuudan வரவேற்கிறோம்.\n\n"
            "Ungaloda movie edit requests, queries, illa feedback-a inge message-ah anuppunga. Seekiram ungalukku reply panrom! ✨"
        )

# User Message Handler
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text
    
    if user.id == ADMIN_CHAT_ID:
        return  # Ignore normal text messages from admin to avoid loops

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

# Global event loop for handling requests safely
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def setup_handlers():
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("reply", reply_to_user))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
    await telegram_app.initialize()
    await telegram_app.start()

# Initialize handlers on startup using the main loop
loop.run_until_complete(setup_handlers())

@app_flask.route('/')
def home():
    return "Bot is alive and running!"

@app_flask.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        json_update = request.get_json(force=True)
        update = Update.de_json(json_update, telegram_app.bot)
        
        # Run update processing inside the persistent global loop
        loop.run_until_complete(telegram_app.process_update(update))
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return "Internal Error", 500

    return "OK", 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app_flask.run(host='0.0.0.0', port=PORT)
    
