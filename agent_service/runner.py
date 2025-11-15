from agent_service.graph import build_graph

graph = build_graph()

def code_runner(user_name:str, user_input:str):
        # fresh state for this run
    state = {
        "query": user_input,
        "chat_history": [],
        "subagent_outputs": [] 
    }

    result = graph.invoke(state)
    final_answer = result["final_response"]

    return final_answer
