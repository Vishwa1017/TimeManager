from dotenv import load_dotenv
from bot.handlers import build_app

load_dotenv()

app = build_app()

print("Telegram bot running...")
app.run_polling()
