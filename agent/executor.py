from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from dotenv import load_dotenv
from agent.tools import (
    get_current_datetime_safe,
    get_calendars_info_safe,
    search_calendar_events,
    create_calendar_event_safe,
    update_calendar_event_safe,
    move_calendar_event_safe,
    delete_calendar_event_safe,
    TIMEZONE,
)

load_dotenv()

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
 - When the user says a task is completed, update the calendar event title by adding [DONE].
 - When the user says a task was not done or missed, update the title by adding [MISSED].
 - Do not create a new event for completion status.
 - Search for the matching event first, then update its title.
"""
)

thread_config = {"configurable": {"thread_id": "1"}}
