from langchain.schema import SystemMessage, HumanMessage
from typing import Dict
from agent_service.prompts import SYNTHESIZER_PROMPT
from agent_service.state import SynthesizerOutput
from agent_service.llm import llm  

# Wrap the LLM
synthesizer_llm = llm.with_structured_output(SynthesizerOutput)

# Synthesizer Node
def synthesizer_node(state: Dict) -> Dict:
    """
    Generate a coherent response from subagent outputs.
    """
    user_query = state["query"]
    chat_history = state.get("chat_history", [])
    subagent_outputs = state.get("subagent_outputs", [])

    # Format chat history
    # chat_str = "\n".join([f"User: {c['user']}\nBot: {c['bot']}" for c in chat_history])

    # Format subagent outputs
    subagent_str = ""
    for sa in subagent_outputs:
        sa_type = sa["type"]
        sa_params = sa.get("parameters", {})
        sa_output = sa.get("output")
        subagent_str += f"\n\n---\nSubagent type: {sa_type}\nParameters: {sa_params}\nOutput: {sa_output}"

    # Construct messages using the separate prompt
    messages = [
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(content=f"Chat history:\n{chat_history}\nUser query: {user_query}\nSubagent outputs:\n{subagent_str}")
    ]

    # Call the LLM
    parsed: SynthesizerOutput = synthesizer_llm.invoke(messages)
    # parsed = llm.invoke(messages)

    # Store in state
    state["final_response"] = parsed.model_dump()["final_answer"]

    return state
