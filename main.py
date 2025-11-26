import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# আপনার টোকেন
TOKEN = "8257636584:AAHjbwZc3CdI2VFH6Z8skd6ePzwpZ_F6zHA"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি এখন Render সার্ভার থেকে চলছি! 🚀")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Render থেকে অটোমেটিক পোর্ট এবং ইউআরএল নেওয়া
    PORT = int(os.environ.get("PORT", "8080"))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL") # Render অটোমেটিক এই লিংক দেয়

    if RENDER_EXTERNAL_URL:
        # যদি সার্ভারে রান হয়
        full_webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Deploying to Render. Webhook: {full_webhook_url}")
        
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=full_webhook_url
        )
    else:
        # যদি আপনি লোকাল পিসিতে টেস্ট করেন (লিংক ছাড়া)
        print("Running Locally (Polling Mode)...")
        application.run_polling()

if __name__ == "__main__":
    main()
