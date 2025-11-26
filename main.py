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
    await update.message.reply_text("হ্যালো! আমি ওয়েবসাইট এবং বট—দুটোই একসাথে চালাচ্ছি! 🚀")

# গ্লোবাল অ্যাপ্লিকেশন অবজেক্ট তৈরি
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
@app.route(f'/{TOKEN}', methods=['POST'])
async def telegram_webhook():
    # সমস্যা সমাধান: এখানে চেক করা হচ্ছে বট চালু আছে কিনা
    if not ptb_application._initialized:
        await ptb_application.initialize()
        await ptb_application.start()

    # টেলিগ্রাম থেকে আসা ডেটা নেওয়া
    json_update = request.get_json(force=True)
    
    # আপডেট তৈরি করা
    update = Update.de_json(json_update, ptb_application.bot)
    
    # বটের মাধ্যমে প্রসেস করা
    await ptb_application.process_update(update)
    
    return "OK"

# --- মেইন ফাংশন ---
if __name__ == "__main__":
    # Render থেকে পোর্ট এবং URL নেওয়া
    PORT = int(os.environ.get("PORT", "8080"))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

    # ওয়েব হুক সেট করার জন্য লুপ চালানো
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Setting webhook to: {webhook_url}")
        
        # বট ইনিশিয়ালাইজ করে হুক সেট করা
        loop = asyncio.get_event_loop()
        
        # হুক সেট করার আগে ইনিশিয়ালাইজ করা জরুরি
        if not ptb_application._initialized:
            loop.run_until_complete(ptb_application.initialize())
            
        loop.run_until_complete(ptb_application.bot.set_webhook(webhook_url))
    else:
        print("Running locally...")

    # Flask সার্ভার রান করা
    app.run(host="0.0.0.0", port=PORT)
    
