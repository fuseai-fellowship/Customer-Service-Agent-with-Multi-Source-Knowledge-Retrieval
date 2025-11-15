from langgraph.types import Send
from agent_service.state import State

def assign_subagents(state: State):
    sends = []

    for qt in state.get("query_types", []):
        if qt["type"] == "menu":
            sends.append(Send("menu_agent", {"params": {k: v for k, v in qt["parameters"].items() if v is not None}}))
        elif qt["type"] == "info":
            sends.append(Send("info_agent", {"params": {k: v for k, v in qt["parameters"].items() if v is not None}}))
        elif qt["type"] == "escalation":
            sends.append(Send("escalation_agent", {"params": qt.get("parameters", {})}))
        elif qt["type"] == "ambiguous":
            # inject synthetic chitchat output for synthesizer, no Send required
            state.setdefault("subagent_outputs", []).append({
                "type": "chitchat",
                "parameters": {},
                "output": qt["clarification"]
            })
        elif qt["type"] == "chitchat":
            # inject synthetic chitchat output for synthesizer, no Send required
            state.setdefault("subagent_outputs", []).append({
                "type": "chitchat",
                "parameters": {},
                "output": None
            })

    # If no subagents were scheduled, explicitly tell the graph to run synthesizer next
    if not sends:
        return [Send("synthesizer", {
                "query": state.get("query"),
                "chat_history": state.get("chat_history", []),
                "subagent_outputs": state.get("subagent_outputs", []),
                "memory_results": state.get("memory_results", [])})]

    return sends
