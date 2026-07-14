from dotenv import load_dotenv
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

from agent.analyzer_agent import analyzer_agent_executor

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_ID")


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text

        response = analyzer_agent_executor.invoke(
            {
                "messages": [
                    ("user", user_message)
                ]
            }
        )

        await update.message.reply_text(
            response["messages"][-1].content
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {str(e)}"
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            analyze,
        )
    )

    print("Analyzer Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()