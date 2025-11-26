import os
import logging
import asyncio
import threading
import queue
from flask import Flask, request, render_template
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# টোকেন
TOKEN = "8257636584:AAHjbwZc3CdI2VFH6Z8skd6ePzwpZ_F6zHA"

# ১. একটি গ্লোবাল বক্স (Queue) তৈরি করা হলো
# Flask এখানে মেসেজ রাখবে, আর Bot এখান থেকে মেসেজ নিয়ে কাজ করবে।
update_queue = queue.Queue()

app = Flask(__name__)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- বটের লজিক ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি ব্যাকগ্রাউন্ড থ্রেড থেকে রিপ্লাই দিচ্ছি! ⚡")

async def bot_loop(application):
    """এটি আলাদা থ্রেডে চলবে এবং কিউ (Queue) চেক করবে"""
    print("Bot Worker: Started & Waiting for messages...")
    
    # বট ইনিশিয়ালাইজ করা
    await application.initialize()
    await application.start()
    
    while True:
        # কিউ থেকে মেসেজ নেওয়া (Blocking call না করে)
        try:
            # কিউ চেক করা (যদি খালি থাকে তবে ১ সেকেন্ড অপেক্ষা করবে)
            update_data = update_queue.get(timeout=1) 
            
            # JSON থেকে আপডেট অবজেক্ট তৈরি
            update = Update.de_json(update_data, application.bot)
            
            # মেসেজ প্রসেস করা
            await application.process_update(update)
            print("Bot Worker: Message Processed!")
            
        except queue.Empty:
            # কিউ খালি থাকলে লুপ ঘুরতে থাকবে, বন্ধ হবে না
            continue
        except Exception as e:
            print(f"Bot Worker Error: {e}")

def run_bot_in_background():
    """এই ফাংশনটি ব্যাকগ্রাউন্ড থ্রেড তৈরি করে"""
    # নতুন ইভেন্ট লুপ তৈরি (আলাদা থ্রেডের জন্য)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # অ্যাপ্লিকেশন বিল্ড করা
    ptb_application = Application.builder().token(TOKEN).build()
    ptb_application.add_handler(CommandHandler("start", start))
    
    # লুপ চালু করা
    loop.run_until_complete(bot_loop(ptb_application))

# --- Flask ওয়েবসাইটের লজিক ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route(f'/{TOKEN}', methods=['POST'])
def telegram_webhook():
    """Flask শুধু মেসেজ রিসিভ করে কিউ-তে রেখে দিবে"""
    try:
        json_update = request.get_json(force=True)
        
        # ১. মেসেজটি কিউ-তে রাখা হলো (বট পরে প্রসেস করবে)
        update_queue.put(json_update)
        
        # ২. টেলিগ্রামকে সাথে সাথে "OK" বলে দেওয়া হলো
        # এতে টেলিগ্রাম ভাববে সার্ভার খুব ফাস্ট এবং টাইমআউট হবে না
        return "OK", 200
        
    except Exception as e:
        print(f"Webhook Error: {e}")
        return "Error", 500

# --- মেইন ---
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", "8080"))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

    # ১. বট ওয়ার্কার চালু করা (আলাদা থ্রেডে)
    # daemon=True মানে হলো মেইন প্রোগ্রাম বন্ধ হলে থ্রেডও বন্ধ হবে
    bot_thread = threading.Thread(target=run_bot_in_background, daemon=True)
    bot_thread.start()

    # ২. ওয়েব হুক সেট করা (মেইন থ্রেড থেকে)
    if RENDER_EXTERNAL_URL:
        # হুক সেট করার জন্য আমাদের একটি টেম্পোরারি সিঙ্ক ফাংশন দরকার
        # কিন্তু আমরা requests লাইব্রেরি দিয়ে সহজভাবে এটি করতে পারি
        import requests
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Setting webhook via requests to: {webhook_url}")
        try:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
        except Exception as e:
            print(f"Webhook setting failed: {e}")
    else:
        print("Running locally...")

    # ৩. Flask সার্ভার রান করা (মেইন থ্রেডে)
    print("Starting Flask Server on Main Thread...")
    app.run(host="0.0.0.0", port=PORT)
    
