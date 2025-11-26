import os
import logging
from flask import Flask, request, render_template
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# আপনার টোকেন
TOKEN = "8257636584:AAHjbwZc3CdI2VFH6Z8skd6ePzwpZ_F6zHA"

# Flask অ্যাপ
app = Flask(__name__)

# লগিং
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# টেলিগ্রাম বটের ফাংশন
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("হ্যালো! আমি ওয়েবসাইট এবং বট—দুটোই একসাথে চালাচ্ছি! 🚀")
    except Exception as e:
        print(f"মেসেজ পাঠাতে সমস্যা হয়েছে: {e}")

# গ্লোবাল অ্যাপ্লিকেশন অবজেক্ট
ptb_application = Application.builder().token(TOKEN).build()
ptb_application.add_handler(CommandHandler("start", start))

# --- ওয়েবসাইটের পেজগুলো ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# --- টেলিগ্রাম ওয়েব হুক রাউট ---
@app.route(f'/{TOKEN}', methods=['POST'])
async def telegram_webhook():
    # ইনিশিয়ালাইজেশন চেক
    if not ptb_application._initialized:
        await ptb_application.initialize()
        await ptb_application.start()

    # আপডেট প্রসেস করা
    try:
        json_update = request.get_json(force=True)
        update = Update.de_json(json_update, ptb_application.bot)
        await ptb_application.process_update(update)
    except RuntimeError as e:
        # লুপ ক্লোজ এরর ইগনোর করা
        if "Event loop is closed" in str(e):
            pass 
        else:
            print(f"Critical Runtime Error: {e}")
    except Exception as e:
        print(f"Other Error: {e}")
        
    return "OK", 200

# --- মেইন ---
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", "8080"))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Setting webhook to: {webhook_url}")
        
        loop = asyncio.get_event_loop()
        if not ptb_application._initialized:
            loop.run_until_complete(ptb_application.initialize())
        loop.run_until_complete(ptb_application.bot.set_webhook(webhook_url))
    else:
        print("Running locally...")

    app.run(host="0.0.0.0", port=PORT)
    
