import json
from agent_service.state import State
from agent_service.utils.compact_menu_summary import compact_menu_summary

def tool_summarizer_node(state:State):
    """
    Summarizes tool messages and appends to state['tool_output'].
    Only includes messages that have a name attribute (i.e., tool outputs).
    """
    state.setdefault("tool_output", "")

    for msg in state.get("messages", []):
        if not hasattr(msg, "name") or not hasattr(msg, "content"):
            continue

        name = msg.name
        content = msg.content

        # Ensure content is a string
        if content is None:
            content = ""
        elif isinstance(content, list):
            content = json.dumps(content) if content else "No matches found."

        if not name:
            continue

        if name == "menu_tool":
            summary_text, overflow = compact_menu_summary(content)
            state["tool_output"] += f"\nmenu_tool output: {summary_text}"
        else:
            state["tool_output"] += f"\n{name} output:\n{content}"


    return state
