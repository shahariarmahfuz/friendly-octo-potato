import os
import logging
from flask import Flask, request, render_template
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# আপনার টোকেন
TOKEN = "8257636584:AAHjbwZc3CdI2VFH6Z8skd6ePzwpZ_F6zHA"

# Flask অ্যাপ তৈরি
app = Flask(__name__)

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# টেলিগ্রাম বটের ফাংশন
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি এখন ওয়েবসাইট এবং বট—দুটোই সামলাচ্ছি! 😎")

# গ্লোবাল অ্যাপ্লিকেশন অবজেক্ট
ptb_application = Application.builder().token(TOKEN).build()
ptb_application.add_handler(CommandHandler("start", start))

# --- ওয়েবসাইটের পেজগুলো (Routes) ---

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
# টেলিগ্রাম সার্ভার এই লিংকেই মেসেজ পাঠাবে
@app.route(f'/{TOKEN}', methods=['POST'])
async def telegram_webhook():
    # টেলিগ্রাম থেকে আসা ডেটা নেওয়া
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, ptb_application.bot)
    
    # বটের মাধ্যমে প্রসেস করা
    await ptb_application.process_update(update)
    return "OK"

# --- মেইন ফাংশন ---
if __name__ == "__main__":
    # Render থেকে পোর্ট এবং URL নেওয়া
    PORT = int(os.environ.get("PORT", "8080"))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

    if RENDER_EXTERNAL_URL:
        # বটের ওয়েব হুক সেট করা
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Setting webhook to: {webhook_url}")
        
        # এখানে আমরা async ফাংশন রান করছি হুক সেট করার জন্য
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ptb_application.bot.set_webhook(webhook_url))
    else:
        print("Running locally...")

    # Flask সার্ভার রান করা
    app.run(host="0.0.0.0", port=PORT)
    
