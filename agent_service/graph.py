from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from nodes import orchestrator, tools_node, reviewer_node, tool_summarizer_node
from state import State


def route_after_reviewer(state: State):
    return "orchestrator_node" if state.get("review_decision") == "needs_more" else "__end__"

def build_graph():
    g = StateGraph(State)

    g.add_node("orchestrator_node", orchestrator)
    g.add_node("tools", tools_node)          # or tools_node.invoke
    g.add_node("reviewer", reviewer_node)
    g.add_node("summarize_menu_tool",tool_summarizer_node)

    g.add_edge(START, "orchestrator_node")

    # If assistant asked for tools, go to tools; otherwise go to reviewer
    g.add_conditional_edges(
        "orchestrator_node",
        tools_condition,
        {"tools": "tools", "__end__": "reviewer"},
    )

    g.add_edge("tools", "summarize_menu_tool")

    g.add_edge("summarize_menu_tool", "reviewer")

    # Reviewer decides whether to loop back or end
    g.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {"orchestrator_node": "orchestrator_node", "__end__": END},
    )

    return g.compile()
