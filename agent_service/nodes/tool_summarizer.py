from agent_service.state import State
from agent_service.utils.compact_menu_summary import compact_menu_summary

def tool_summarizer_node(state:State):
    """
    Summarizes tool messages and appends to state['summary'].
    Detects tool messages dynamically by checking for 'name' and 'content' attributes.
    """
    state.setdefault("summary", "")

    for msg in state.get("messages", []):
        # dynamically detect tool messages
        if not hasattr(msg, "name") or not hasattr(msg, "content"):
            continue

        content = msg.content
        name = msg.name
        if not content or not name:
            continue

        if name == "menu_tool":
            summary_text, overflow = compact_menu_summary(content)
            state["summary"] += f"\nmenu_tool summary:\n{summary_text}"
        else:
            state["summary"] += f"\n{name} output:\n{content}"
        

    return {"summary": state["summary"]}
