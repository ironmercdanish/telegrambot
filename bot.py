import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load token
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Set your ADMIN ID (replace with your real chat_id)
ADMIN_ID = 7592315694  # apna ID daalna

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! 👋 I’m your new bot.")

# Handle all messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text or ""

    # Agar user (non-admin) message bhejta hai → forward to admin
    if chat_id != ADMIN_ID:
        msg = f"📩 New message from {user.first_name} ({chat_id})"
        if text:
            msg += f"\n{text}"
            await context.bot.send_message(ADMIN_ID, msg)

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(ADMIN_ID, file_id, caption=f"From {user.first_name} ({chat_id})")

        if update.message.document:
            file_id = update.message.document.file_id
            await context.bot.send_document(ADMIN_ID, file_id, caption=f"From {user.first_name} ({chat_id})")

    # Agar admin /reply se message bhejta hai
    elif text.startswith("/reply"):
        try:
            parts = text.split(" ", 2)
            user_id = int(parts[1])
            reply_text = parts[2]
            await context.bot.send_message(user_id, reply_text)
            await update.message.reply_text(f"✅ Sent to {user_id}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")

    # Agar admin photo bhejta hai → usko /reply ke sath bhejna padega
    elif chat_id == ADMIN_ID and (update.message.photo or update.message.document):
        try:
            parts = update.message.caption.split(" ", 2) if update.message.caption else []
            if len(parts) >= 2 and parts[0] == "/reply":
                user_id = int(parts[1])

                if update.message.photo:
                    file_id = update.message.photo[-1].file_id
                    await context.bot.send_photo(user_id, file_id, caption=(parts[2] if len(parts) > 2 else ""))

                if update.message.document:
                    file_id = update.message.document.file_id
                    await context.bot.send_document(user_id, file_id, caption=(parts[2] if len(parts) > 2 else ""))

                await update.message.reply_text(f"✅ Media sent to {user_id}")
            else:
                await update.message.reply_text("⚠️ Agar media bhejna hai to caption me likho: /reply <user_id> <optional_text>")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")

def main():
    if not BOT_TOKEN:
        raise ValueError("⚠️ No TELEGRAM_BOT_TOKEN found. Check your .env file!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    logger.info("🚀 Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
