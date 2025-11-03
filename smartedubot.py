import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# 📜 Լոգերի կարգավորում
logging.basicConfig(level=logging.INFO)

# 🔑 Ստանում ենք բանալիները Render միջավայրից
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    raise RuntimeError("❌ OPENAI_API_KEY կամ TELEGRAM_TOKEN միջավայրում չկան։")

# 🧠 OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# 👋 Start հրաման
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարև 👋 Ես SmartEduBot-ն եմ։ Ուղարկիր որևէ հարց — մաթեմատիկա, ֆիզիկա, քիմիա և այլն։")


# 💬 Հաղորդագրությունների պատասխանում
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Դու կրթական օգնական ես։ Պատասխանիր հակիրճ և ճշգրիտ։"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)
    except Exception as e:
        logging.error(f"❌ OPENAI ERROR: {e}")
        await update.message.reply_text("⚠️ Սխալ տեղի ունեցավ։ Փորձիր կրկին։")


# 🚀 Գլխավոր ֆունկցիա
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handler-ներ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 SmartEduBot is running...")
    app.run_polling()  # ✅ սա նոր ձևն է (Updater այլևս պետք չէ)


if __name__ == "__main__":
    main()
