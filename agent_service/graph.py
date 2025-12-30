from langgraph.graph import StateGraph, START, END
from agent_service.nodes import orchestrator_node, menu_agent, info_agent, synthesizer_node, escalation_agent
from agent_service.state import State
from agent_service.utils.assign_subagents import assign_subagents


def build_graph():

    # Build the workflow
    workflow_builder = StateGraph(State)

    # Add nodes
    workflow_builder.add_node("orchestrator", orchestrator_node)
    workflow_builder.add_node("menu_agent", menu_agent)
    workflow_builder.add_node("info_agent", info_agent)
    workflow_builder.add_node("escalation_agent", escalation_agent)
    workflow_builder.add_node("synthesizer", synthesizer_node)

    # Start edge
    workflow_builder.add_edge(START, "orchestrator")

    workflow_builder.add_conditional_edges("orchestrator", assign_subagents, ["menu_agent", "info_agent", "escalation_agent"])

    # Collect subagent outputs and send to synthesizer
    workflow_builder.add_edge("menu_agent", "synthesizer")
    workflow_builder.add_edge("info_agent", "synthesizer")
    workflow_builder.add_edge("escalation_agent", "synthesizer")

    # End edge
    workflow_builder.add_edge("synthesizer", END)

    return workflow_builder.compile()

