from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field


load_dotenv()


class TaskInstruction(BaseModel):
    action: str = Field(
        description="Calendar action: create, update, delete, complete, miss, or query"
    )
    title: str = Field(
        description="Event title exactly as written by the user"
    )
    description: str | None = Field(
        default=None,
        description="Additional task details, or null if none were provided"
    )
    start_time: str | None = Field(
        default=None,
        description="Start date or time exactly as written, or null"
    )
    end_time: str | None = Field(
        default=None,
        description="End date or time exactly as written, or null"
    )


class TaskInstructionList(BaseModel):
    tasks: list[TaskInstruction]


model = init_chat_model(
    "gpt-4o-mini",
    temperature=0,
)

structured_model = model.with_structured_output(TaskInstructionList)


def clean_instructions(instructions: str) -> TaskInstructionList:
    system_prompt = """
You are an Intent Extraction AI.

Extract structured calendar requests from the user's message.

Split multiple intentions into separate task objects.

Supported actions:
- create
- update
- delete
- complete
- miss
- query

Rules:
- Each task represents exactly one intention.
- Preserve event titles exactly as written.
- Do not rename or improve titles.
- Do not resolve relative dates such as today, tomorrow, or next Monday.
- Keep dates and times exactly as written.
- Use null when information is missing.
- Never guess or fabricate information.
- Never answer conversationally.
- Only return data matching the supplied schema.
"""

    result = structured_model.invoke(
        [
            ("system", system_prompt),
            ("user", instructions),
        ]
    )

    return result