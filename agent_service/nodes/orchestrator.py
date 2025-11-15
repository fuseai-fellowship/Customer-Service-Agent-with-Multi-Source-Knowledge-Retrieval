from langchain.schema import HumanMessage, SystemMessage, AIMessage
from agent_service.llm import llm
from agent_service.state import State, OrchestratorOutput
from agent_service.prompts import ORCHESTRATOR_PROMPT

orchestrator_llm = llm.with_structured_output(OrchestratorOutput)

# Orchestrator Node
def orchestrator_node(state: State):
    """Classify user query and extract menu parameters for subagents."""

    # Construct LLM messages
    messages = [
        SystemMessage(content=ORCHESTRATOR_PROMPT),
        HumanMessage(content=f"Chat history:{state["chat_history"]}"),
        HumanMessage(content=state["query"])
    ]

    # Call the LLM (replace `llm` with your LangChain/LLM client)
    parsed: OrchestratorOutput = orchestrator_llm.invoke(messages)  # Should return JSON string

    state["query_types"] = parsed.model_dump()["query_types"]

    return state

test_state = {
    "query": "wht kind of pizza you got maybe with chicken also are you open at 5pm",
    "chat_history": [
        {"user": "Hi", "bot": "Hello! How can I help you today?"},
        {"user": "I want to know your menu.", "bot": "Sure, what type of dishes are you interested in?"}
    ]
}
resp = orchestrator_node(test_state)
print(resp['query_types'])