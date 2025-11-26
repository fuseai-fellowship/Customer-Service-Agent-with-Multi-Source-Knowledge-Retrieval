from agent_service.graph import build_graph
from agent_service.utils.redis import save_message, load_history

graph = build_graph()

def interactive_loop(user_id="user03", user_name="camus"):
    print("Chat loop (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not user_input:
            continue

        # Load history for this user
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

        # Print assistant's reply
        print("\nAssistant:", final_answer)

        # Save the assistant's reply
        save_message(user_id, "assistant", final_answer)

        print()  # blank line for readability

if __name__ == "__main__":
    interactive_loop()
