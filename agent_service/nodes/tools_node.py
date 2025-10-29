from agent_service.tools import menu_tool, kb_tool
from langgraph.prebuilt import ToolNode

tools = [menu_tool, kb_tool]
tools_node = ToolNode(tools=tools)