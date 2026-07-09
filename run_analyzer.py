from agent.analyzer_agent import analyzer_agent_executor

result = analyzer_agent_executor.invoke(
            {
                "messages": [
                    ("user", "Summarize today")
                ]
            }
        )

print(result["messages"][-1].content)