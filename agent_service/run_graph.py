from agent_service.graph import build_graph
from langchain.schema import HumanMessage

graph = build_graph()

# user query
user_input = "what do you guys have momo?"
human_msg = HumanMessage(content=user_input)

# ensure state exists
state = {
    "messages": [],
    "summary": ""
}

# append human message to messages and summary
state["messages"].append(human_msg)
state["summary"] += f"\nHuman: {human_msg.content}"

# now invoke your graph with updated state
result = graph.invoke(state)
print(result["messages"][-1].content)