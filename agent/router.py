from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from typing import Literal
from agent.memory import checkpointer

load_dotenv()

class RouterDecision(BaseModel): 
    destination : Literal["calendar","analyzer"] = Field(
        description="The agent that should handle the user's request"
    )

    reason: str = Field(
        description="A short explanation for the routing decision"
    )


model = init_chat_model(
    "gpt-4o-mini")

router_model  = model.with_structured_output(RouterDecision)

def route_message(message: str) -> RouterDecision:
    system_prompt = """
You are the routing component of a time-management assistant.

Choose exactly one destination:

calendar:
Use for requests that create, update, delete, complete, miss,
search, or query calendar events and tasks.

analyzer:
Use for requests asking for productivity analysis, motivation,
performance feedback, summaries, execution ratio, missed-task
analysis, priorities, or recommendations based on the calendar.

Examples:

"Create a gym event tomorrow at 5 PM"
destination: calendar

"Delete my meeting tomorrow"
destination: calendar

"What events do I have today?"
destination: calendar

"Analyze my productivity today"
destination: analyzer

"Motivate me based on my performance"
destination: analyzer

"How many tasks did I complete this week?"
destination: analyzer

Return only data matching the supplied schema.
"""

    return router_model .invoke(
        [
            ("system", system_prompt),
            ("user", message),
        ]
    )

