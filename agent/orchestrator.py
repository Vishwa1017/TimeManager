from agent.analyzer_agent import analyzer_agent_executor
from agent.executor import agent_executor
from agent.router import route_message
from utils.instructions import clean_instructions
from utils.logger import get_logger


logger = get_logger(__name__)


def orchestrator(message: str, user_id: int) -> str:
    try:
        route = route_message(message)

        logger.info(
            "Router selected destination=%s reason=%s user_id=%s",
            route.destination,
            route.reason,
            user_id,
        )

    except Exception:
        logger.exception(
            "Router failed user_id=%s",
            user_id,
        )

        return (
            "I could not understand how to process your request. "
            "Please try again."
        )

    thread_config = {
        "configurable": {
            "thread_id": f"{user_id}-{route.destination}"
        }
    }

    try:
        if route.destination == "analyzer":
            response = analyzer_agent_executor.invoke(
                {
                    "messages": [
                        ("user", message)
                    ]
                },
                config=thread_config,
            )

        elif route.destination == "calendar":
            instructions = clean_instructions(message)

            response = agent_executor.invoke(
                {
                    "messages": [
                        (
                            "user",
                            instructions.model_dump_json(),
                        )
                    ]
                },
                config=thread_config,
            )

        else:
            logger.warning(
                "Unsupported destination=%s user_id=%s",
                route.destination,
                user_id,
            )

            return "The selected agent is not supported."

    except Exception:
        logger.exception(
            "Agent execution failed destination=%s user_id=%s",
            route.destination,
            user_id,
        )

        return (
            f"The {route.destination} agent could not complete "
            "your request."
        )

    try:
        messages = response.get("messages")

        if not messages:
            raise ValueError("Agent returned no messages")

        final_content = messages[-1].content

        if not final_content:
            raise ValueError("Agent returned empty content")

        return final_content

    except Exception:
        logger.exception(
            "Failed to extract response destination=%s user_id=%s",
            route.destination,
            user_id,
        )

        return (
            "The operation may have completed, but I could not "
            "read the final response."
        )