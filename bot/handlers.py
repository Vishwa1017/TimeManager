from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from agent.executor import agent_executor, thread_config
from utils.instructions import clean_instructions
import os


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        cleaned = clean_instructions(user_text)

        result = agent_executor.invoke(
            {
                "messages": [
                    (
                        "user",
                        cleaned.model_dump_json()
                    )
                ]
            }
        )

        response = result["messages"][-1].content
        await update.message.reply_text(response)

    except Exception as e:
        print(f"{type(e).__name__}: {e}")

        await update.message.reply_text(
            f"An internal error occurred: {type(e).__name__}"
        )

def build_app():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )
    return app
