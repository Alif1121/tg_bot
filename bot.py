from flask import Flask, request
from telegram import Update, Poll, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import asyncio

TOKEN = "7894908322:AAFlE-dVgawzrmGTtkloJ_D9CaR_4b6nXAI"
app = Flask(__name__)

# Bot and Application instance globally (create application once)
application = ApplicationBuilder().token(TOKEN).build()

def parse_full_format(text):
    lines = text.strip().split("\n")
    question = ""
    explanation = ""
    options = []
    answer_index = None
    for line in lines:
        if line.startswith("প্রশ্ন -"):
            question = line.replace("প্রশ্ন -", "").strip()
        elif line.startswith("ব্যাখা -"):
            explanation = line.replace("ব্যাখা -", "").strip()
        elif line.strip() and line[0].isdigit() and "." in line:
            # Option line like "১. Option text"
            options.append(line.split(". ", 1)[1])
        elif line.startswith("উত্তর -"):
            try:
                answer_index = int(line.replace("উত্তর -", "").strip()) - 1
            except:
                answer_index = None
    if question and options and answer_index is not None and 0 <= answer_index < len(options):
        return question, options, answer_index, explanation
    else:
        return None, None, None, None

# async handlers according to v20+
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 কুইজ পাঠাতে চাইলে এই ফরম্যাটে পাঠাও:\n\n"
        "প্রশ্ন - প্রশ্ন লিখো\n"
        "ব্যাখা - ব্যাখ্যা লিখো (ঐচ্ছিক)\n"
        "১. অপশন ১\n"
        "২. অপশন ২\n"
        "৩. অপশন ৩\n"
        "৪. অপশন ৪\n"
        "উত্তর - সঠিক অপশন নম্বর\n\n"
        "উদাহরণ:\n"
        "প্রশ্ন - মুক্তিযুদ্ধ কবে শুরু হয়?\n"
        "ব্যাখা - এটি ছিল পাকিস্তানি শাসনের বিরুদ্ধে যুদ্ধ।\n"
        "১. ১৯৬৯\n"
        "২. ১৯৭১\n"
        "৩. ১৯৭৫\n"
        "৪. ১৯৭০\n"
        "উত্তর - ২"
    )

async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    question, options, correct_index, explanation = parse_full_format(text)
    if question and options and correct_index is not None:
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            type=Poll.QUIZ,
            correct_option_id=correct_index,
            is_anonymous=False,
        )
        await update.message.reply_text(
            f"✅ সঠিক উত্তর: {correct_index + 1}. {options[correct_index]}\n📘 ব্যাখা: {explanation if explanation else 'প্রদান করা হয়নি।'}"
        )
    else:
        await update.message.reply_text("❌ ফরম্যাট ঠিক নয়। দয়া করে সঠিকভাবে প্রশ্ন, অপশন এবং উত্তর দাও।")

# Add handlers to application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quiz_handler))


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # Flask runs on port 5000 by default; Railway assigns PORT env var, use that in production
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)