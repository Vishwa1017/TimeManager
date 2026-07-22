from utils.instructions import clean_instructions
from agent.executor import agent_executor, thread_config
from agent.analyzer_agent import analyzer_agent_executor
from agent.router import route_message


def orchestrator(message: str) -> str:
    route_decision = route_message(message)

    if route_decision.destination == "analyzer":
        response = analyzer_agent_executor.invoke(
            { 
                "messages" :[
                    ("user", "Analyze")
                ]
            },
            config=thread_config
        )
    else:
        instructions = clean_instructions(message)

        response = agent_executor.invoke(
        {
            "messages": [
                (
                    "user",
                    instructions.model_dump_json()
                )
            ]
        },
        config=thread_config
    )

    return response["messages"][-1].content