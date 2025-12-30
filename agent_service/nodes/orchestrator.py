from langchain.schema import HumanMessage, SystemMessage, AIMessage
from agent_service.llm import llm
from agent_service.state import State, OrchestratorOutput
from agent_service.prompts import ORCHESTRATOR_PROMPT

orchestrator_llm = llm.with_structured_output(OrchestratorOutput)

# Orchestrator Node
def orchestrator_node(state: State):
    """Classify user query and extract menu parameters for subagents."""

    user_query = state["query"]
    chat_history = state.get("chat_history", [])
    # Construct LLM messages
    messages = [
        SystemMessage(content=ORCHESTRATOR_PROMPT),
        HumanMessage(content=f"Chat history:\n{chat_history}\nUser query: {user_query}")
    ]

    # Call the LLM (replace `llm` with your LangChain/LLM client)
    parsed: OrchestratorOutput = orchestrator_llm.invoke(messages)  # Should return JSON string

    state["query_types"] = parsed.model_dump()["query_types"]

    return state

