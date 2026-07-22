from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from agent.executor import agent_executor, thread_config
from utils.instructions import clean_instructions
from agent.orchestrator import orchestrator
import os

group_chat_id = os.getenv("TELEGRAM_GROUP_ID")

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        user_text = update.message.text
        orchestrator_response = orchestrator(user_text)

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=orchestrator_response,
        )

    except Exception as error:
        print(f"TELEGRAM HANDLER ERROR → {error}")

        await update.message.reply_text(
            "The bot encountered an unexpected error."
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
