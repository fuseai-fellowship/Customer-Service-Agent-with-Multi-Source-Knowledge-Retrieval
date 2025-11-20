from agent_service.graph import build_graph
from agent_service.utils.redis import save_message,load_history

graph = build_graph()

def code_runner(user_name:str, user_input:str, user_id:str):
        # fresh state for this run
    chat_history = load_history(user_id)

    # Save the user's new message
    save_message(user_id, "user", user_input)
    
    # Fresh state for this run
    state = {
        "query": user_input,
        "chat_history": chat_history,
        "subagent_outputs": [],
        "user_id": user_id,
        "user_name": user_name
    }
    
    # Invoke the graph
    result = graph.invoke(state)
    final_answer = result.get("final_response", "(no response)")

    # Save the assistant's reply
    save_message(user_id, "assistant", final_answer)

    return final_answer
