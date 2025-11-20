from langgraph.types import Send
from agent_service.state import State

def assign_subagents(state: State):
    sends = []

    for qt in state.get("query_types", []):
        qtype = qt.get("type")
        raw_params = qt.get("parameters") or {}
        parameters = {k: v for k, v in raw_params.items() if v is not None}

        if qtype == "menu":
            sends.append(Send("menu_agent", {"params": parameters}))

        elif qtype == "info":
            sends.append(Send("info_agent", {"params": parameters}))

        elif qtype == "escalation":
            esc_params = parameters.copy()
            esc_params["user_name"] = state.get("user_name")
            sends.append(Send("escalation_agent", {"params": esc_params}))

        elif qt["type"] == "ambiguous":
            state.setdefault("subagent_outputs", []).append({
                "type": "ambiguous",
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
