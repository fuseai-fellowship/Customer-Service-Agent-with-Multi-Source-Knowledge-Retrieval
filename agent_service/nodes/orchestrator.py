from agent_service.prompts import ORCHESTRATOR_PROMPT
from agent_service.state import State
from agent_service.llm import llm
from langchain.schema import SystemMessage, AIMessage
from agent_service.tools import menu_tool, kb_tool
tools = [menu_tool, kb_tool]


def orchestrator(state: State):
    """
    Node to classify user intent using the LLM with tools.
    Updates state['messages'] and state['summary'] in-place.
    """
    state.setdefault("summary", "")
    messages = [SystemMessage(content=ORCHESTRATOR_PROMPT)]

    if state.get("summary"):
        messages.append(SystemMessage(content=f"Summary:\n{state['summary']}"))

    if state.get("review_decision"):
        review_dict = state["review_decision"].model_dump() if hasattr(state["review_decision"], "model_dump") else state["review_decision"]
        messages.append(SystemMessage(content=f"Review Decision:\n{review_dict}"))

    # call LLM with tools
    llm_with_tools = llm.bind_tools(tools)
    resp = llm_with_tools.invoke(messages)

    # append AIMessage content to summary
    if isinstance(resp, AIMessage) and getattr(resp, "content", ""):
        state["summary"] += f"\nTool agent output: {resp.content}"

    # append response to messages
    state["messages"].append(resp)

    # return minimal dict; state is already updated
    return state

