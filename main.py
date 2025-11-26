import os
import logging
from flask import Flask, request, render_template
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# আপনার টোকেন
TOKEN = "8257636584:AAHjbwZc3CdI2VFH6Z8skd6ePzwpZ_F6zHA"

app = Flask(__name__)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি রেডি আছি! 🚀")

# অ্যাপ্লিকেশন তৈরি
ptb_application = Application.builder().token(TOKEN).build()
ptb_application.add_handler(CommandHandler("start", start))

# --- হেল্পার ফাংশন: বট রেডি করা ---
async def initialize_bot():
    """বট যদি রেডি না থাকে, তবে রেডি করবে"""
    if not ptb_application._initialized:
        try:
            await ptb_application.initialize()
            await ptb_application.start()
            print("Bot initialized successfully via Website Hit!")
        except Exception as e:
            print(f"Init Error: {e}")

# --- ওয়েবসাইটের পেজ (এখানেই ম্যাজিক হবে) ---
# যখনই কেউ হোমপেজে আসবে, বট ব্যাকগ্রাউন্ডে রেডি হয়ে যাবে
@app.route('/')
async def home():
    # ওয়েবসাইট লোড হওয়ার সাথে সাথে বট রেডি করা হচ্ছে
    await initialize_bot()
    return render_template('home.html')

@app.route('/about')
async def about():
    # অন্য পেজে গেলেও যাতে রেডি হয়
    await initialize_bot()
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# --- টেলিগ্রাম ওয়েব হুক ---
@app.route(f'/{TOKEN}', methods=['POST'])
async def telegram_webhook():
    # ব্যাকআপ: যদি কেউ ওয়েবসাইট না ভিজিট করে সরাসরি মেসেজ দেয়
    await initialize_bot()

    try:
        json_update = request.get_json(force=True)
        update = Update.de_json(json_update, ptb_application.bot)
        
        # মেসেজ প্রসেস করা
        await ptb_application.process_update(update)
    
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            pass
    except Exception as e:
        print(f"Error: {e}")
        
    return "OK", 200

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", "8080"))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Deploying logic... Webhook: {webhook_url}")
        
        # সার্ভার রান হওয়ার সময় একবার ইনিশিয়ালাইজ করার চেষ্টা
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(initialize_bot())
            loop.run_until_complete(ptb_application.bot.set_webhook(webhook_url))
        except Exception as e:
            print(f"Startup Error: {e}")
    else:
        print("Local Mode...")

    app.run(host="0.0.0.0", port=PORT)
    
