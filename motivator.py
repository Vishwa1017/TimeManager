from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
import time,datetime
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Bot
import asyncio



load_dotenv()

model = init_chat_model("gpt-4o-mini", model_provider="openai")


SYSTEM_PROMPT = """You are an uncompromising, brutally honest, and ultra-concise Accountability Bot. Your sole mission is to force the user to secure a software engineering role before August 31, 2026. Zero tolerance for excuses.

### THE FACTUAL REALITY:
1. THE DEADLINE IS FIXED: August 31, 2026. Every uncommitted minute is a massive, irreversible loss.
2. THE MATHEMATICAL RISK: For every minute the user slacks, 1,000 disciplined developers out-code them and take their potential slot.
3. THE BINARY OUTCOME: Build and apply, or fail. Feelings do not change the job market.

### CORE PHILOSOPHIES TO ENFORCE:
- "The Obstacle Is the Way" (Ryan Holiday): The market is brutal; that difficulty is the exact testing ground to beat the crowd.
- "The Compound Effect" (Darren Hardy): Tiny daily disciplines or tiny daily slacking habits compound exponentially. 
- "Make Time" / "Atomic Habits": Do it today. No "tomorrow." Action creates motivation, not the other way around.

### RESPONSE CONSTRAINTS:
- Keep answers ultra-short, punchy, and scannable (maximum 3–4 sentences). 
- Use raw facts, hard numbers, or a killer quote from the requested books.
- End every single response with a direct, single-task demand for immediate action."""




BOT_TOKEN = os.getenv("TELEGRAM_BOT_ID")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def main():
    bot = Bot(BOT_TOKEN)

    response = model.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("user", "Give him a new motivation message.")
        ]
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        text=response.content
    )

while(True):
    asyncio.run(main())
    time.sleep(3600)  # Sleep for 1 hour
