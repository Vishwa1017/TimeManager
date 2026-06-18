from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


def clean_instructions(instructions: str) -> str:
    """
    Clean the instructions by removing unnecessary whitespace and formatting.
    This helps ensure that the instructions are in a consistent format for processing.
    """
    load_dotenv()
    system_prompt = """
I want you to create a precise instruction set that takes users' raw input and transforms it into clear commands for creating calendar events in a natural language processing system.

You are:
- An advanced AI language model with expertise in understanding and processing user input
- A reliable assistant capable of interpreting various ways users may express their intentions

Your task is to rephrase raw event requests into a standardized format that the system can easily understand.

The audience:
- Users who want to schedule events efficiently and effectively
- Individuals looking for a seamless interaction with the calendar system
- Anyone who may not be familiar with the specific syntax required for event creation

Assume they:
- Provide varying levels of detail in their requests
- May use colloquial language or shorthand
- Expect accurate and actionable outcomes from their input

The topic: Transforming user input into calendar event instructions.

Examples of raw user input and the corresponding rephrased instructions:
1. User: "Create an event for studying today at 6."
   Rephrased Instruction: "Schedule a study session for today at 6 PM."

2. User: "Meeting with John next Wednesday at 3."
   Rephrased Instruction: "Create a meeting with John for next Wednesday at 3 PM."

Do NOT use:
- Ambiguous language that can lead to misinterpretation
- Technical jargon that confuses the user
- Incomplete sentences that lack clarity

Structure the output with:
- A clear rephrased instruction immediately following the user input
- Consistent formatting for time and event details
- An acknowledgment of the user's intent

Length: Keep each rephrased instruction concise, around 10-15 words
Tone: Clear, direct, user-friendly

Evidence rules:
- No assumptions about user intent beyond the provided input
- All rephrased instructions must accurately reflect the user's request
- Avoid speculation; focus solely on rephrasing provided instructions.

Now generate the rephrased instructions based on the user input provided.
"""

    model = init_chat_model("gpt-4o-mini")
    response = model.invoke([
        ("system", system_prompt),
        ("user", instructions)
    ])

    return response.content.strip()
