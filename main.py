from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_google_community import CalendarToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from instruction_reschedular import clean_instructions




load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TIMEZONE = "America/Toronto"
PRIMARY_CALENDAR_ID = "viswa3388@gmail.com"

toolkit = CalendarToolkit()
raw_tools = toolkit.get_tools()

raw = {t.name: t for t in raw_tools}

create_raw = raw["create_calendar_event"]
search_raw = raw["search_events"]
update_raw = raw["update_calendar_event"]
move_raw = raw["move_calendar_event"]
delete_raw = raw["delete_calendar_event"]
calendar_info_raw = raw["get_calendars_info"]
current_datetime_raw = raw["get_current_datetime"]

def clean_datetime(dt: str) -> str:
    return (
        dt.replace("T", " ")
        .replace("-04:00", "")
        .replace("-05:00", "")
        .replace("+00:00", "")
        .strip()
    )


@tool
def get_current_datetime_safe() -> str:
    """Get the current date and time in America/Toronto."""
    now = datetime.now(ZoneInfo(TIMEZONE))
    return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def get_calendars_info_safe() -> str:
    """Get available Google Calendar information."""
    return calendar_info_raw.invoke({})


@tool
def search_calendar_events(
    min_datetime: str,
    max_datetime: str,
    max_results: int = 20
) -> str:
    """
    Search calendar events between min_datetime and max_datetime.
    Format: YYYY-MM-DD HH:MM:SS.
    """

    payload = {
        "calendars_info": json.dumps([
            {
                "id": PRIMARY_CALENDAR_ID,
                "summary": PRIMARY_CALENDAR_ID,
                "timeZone": TIMEZONE
            }
        ]),
        "min_datetime": clean_datetime(min_datetime),
        "max_datetime": clean_datetime(max_datetime),
        "max_results": max_results
    }

    print("SEARCH PAYLOAD:", payload)
    return search_raw.invoke(payload)


@tool
def create_calendar_event_safe(
    title: str,
    start_datetime: str,
    end_datetime: str
) -> str:
    """
    Create a calendar event.
    Format: YYYY-MM-DD HH:MM:SS.
    """

    payload = {
        "calendar_id": "primary",
        "summary": title,
        "start_datetime": clean_datetime(start_datetime),
        "end_datetime": clean_datetime(end_datetime),
        "timezone": TIMEZONE
    }

    print("CREATE PAYLOAD:", payload)
    return create_raw.invoke(payload)


@tool
def update_calendar_event_safe(
    event_id: str,
    title: str,
    start_datetime: str,
    end_datetime: str
) -> str:
    """
    Update an existing calendar event.
    Requires event_id. Search events first if event_id is unknown.
    """

    payload = {
        "calendar_id": "primary",
        "event_id": event_id,
        "summary": title,
        "start_datetime": clean_datetime(start_datetime),
        "end_datetime": clean_datetime(end_datetime),
        "timezone": TIMEZONE
    }

    print("UPDATE PAYLOAD:", payload)
    return update_raw.invoke(payload)


@tool
def move_calendar_event_safe(
    event_id: str,
    destination_calendar_id: str = "primary"
) -> str:
    """
    Move an event to another calendar.
    Usually destination_calendar_id should stay primary.
    """

    payload = {
        "calendar_id": "primary",
        "event_id": event_id,
        "destination_calendar_id": destination_calendar_id
    }

    print("MOVE PAYLOAD:", payload)
    return move_raw.invoke(payload)


@tool
def delete_calendar_event_safe(event_id: str) -> str:
    """
    Delete a calendar event.
    Requires event_id. Search events first if event_id is unknown.
    """

    payload = {
        "calendar_id": "primary",
        "event_id": event_id
    }

    print("DELETE PAYLOAD:", payload)
    return delete_raw.invoke(payload)


model = init_chat_model("gpt-4o-mini", model_provider="openai")

agent_executor = create_agent(
    model,
    [
        get_current_datetime_safe,
        get_calendars_info_safe,
        search_calendar_events,
        create_calendar_event_safe,
        update_calendar_event_safe,
        move_calendar_event_safe,
        delete_calendar_event_safe,
    ],

    system_prompt=f"""
You are a Google Calendar assistant.

Current timezone: {TIMEZONE}.

Rules:
- Always call get_current_datetime_safe before resolving relative dates like today, tomorrow, next Monday, after 2pm, this evening.
- Use search_calendar_events to list or find events.
- Use create_calendar_event_safe to create events.
- Use update_calendar_event_safe to edit event title/time.
- Use delete_calendar_event_safe to delete events.
- If event_id is unknown, search first, then use the matching event_id.
- Datetime format must be: YYYY-MM-DD HH:MM:SS.
- Do not use ISO T format.
"""
)

thread_config = {"configurable": {"thread_id": "1"}}

# while True:
#     example_query = input("Ask calendar question: ")

#     if example_query.lower() in ["exit", "quit"]:
#         break

#     try:
#         result = agent_executor.invoke(
#             {"messages": [("user", example_query)]}
#         )

#         print(result["messages"][-1].content)

#     except Exception as e:
#         print("ERROR:", e)

#     print("---------------------------------------------------")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    try:
        result = agent_executor.invoke(
            {
                "messages": [
                    ("user", clean_instructions(user_text))
                ]
            }

        )

        response = result["messages"][-1].content

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("Telegram bot running...")
app.run_polling()