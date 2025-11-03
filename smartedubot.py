import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request

# Load .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # օրինակ՝ https://smartedubot.onrender.com

if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not WEBHOOK_URL:
    raise RuntimeError("❌ TELEGRAM_TOKEN, OPENAI_API_KEY կամ WEBHOOK_URL բացակայում են")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարի գալուստ 🚀 SmartEduBot պատրաստ է օգնելու։")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action("typing")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_text}]
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("⚠️ Սխալ տեղի ունեցավ․ փորձիր նորից։")
        print("❌ OPENAI ERROR:", e)


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@app.route("/" + TELEGRAM_TOKEN, methods=["POST"])
def receive_update():
    """Receive Telegram webhook updates"""
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    return "🤖 SmartEduBot Webhook is running!"


if __name__ == "__main__":
    import asyncio

    async def set_webhook():
        await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")

    asyncio.run(set_webhook())
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}",
    )

