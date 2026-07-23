from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from agent.executor import agent_executor
from utils.instructions import clean_instructions
from agent.orchestrator import orchestrator 
import os
from utils.logger import get_logger

logger = get_logger(__name__)

group_chat_id = os.getenv("TELEGRAM_GROUP_ID")

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        if update.message is None or update.message.text is None:
            logger.warning("Received update without text message")
            return
        if update.effective_user is None:
            await update.message.reply_text(
            "I could not identify the Telegram user."
        )
            return
        user_text = update.message.text.strip()
        user_id = update.effective_user.id

        if not user_text:
            await update.message.reply_text(
                "Please send a valid message."
            )
            return

        logger.info(
            "Received Telegram message user_id=%s chat_id=%s",
            user_id,
            update.effective_chat.id if update.effective_chat else None,
        )

        response = orchestrator(user_text,user_id)

        await context.bot.send_message(
            chat_id=group_chat_id,
            text=response,
        )

    except Exception:
        logger.exception("Telegram handler failed")

        if update.message:
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
