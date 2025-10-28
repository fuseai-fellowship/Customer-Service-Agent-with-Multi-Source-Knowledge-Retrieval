from agent_service.prompts import ORCHESTRATOR_PROMPT
from agent_service.state import State
from agent_service.llm import llm
from agent_service.tools import menu_tool, kb_tool
tools = [menu_tool, kb_tool]

from langchain.schema import SystemMessage, AIMessage

def orchestrator(state: State):
    """
    Node to classify user intent using the LLM with tools.
    Updates state['messages'] and state['summary'] in-place.
    """
    # ensure summary exists
    state.setdefault("summary", "")

    # prepend system prompt to conversation
    messages = [SystemMessage(content=ORCHESTRATOR_PROMPT)] + state["messages"]

    # call LLM with tools
    llm_with_tools = llm.bind_tools(tools)
    resp = llm_with_tools.invoke(messages)

    # append AIMessage content to summary
    if isinstance(resp, AIMessage) and getattr(resp, "content", ""):
        state["summary"] += f"\nAI: {resp.content}"

    # append response to messages
    state["messages"].append(resp)

    # return minimal dict; state is already updated
    return {"messages": [resp]}
