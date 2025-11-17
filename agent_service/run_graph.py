from agent_service.graph import build_graph
from agent_service.utils.redis import save_message, load_history


graph = build_graph()
chat_history = []


def interactive_loop():
    print("Chat loop (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not user_input:
            continue

        chat_history = load_history()
        save_message("user", user_input)
        
        # fresh state for this run
        state = {
            "query": user_input,
            "chat_history": chat_history,
            "subagent_outputs": [] 
        }
     
        # invoke graph
        result = graph.invoke(state)
        final_answer = result["final_response"]

        # Print assistant's reply
        print("\nAssistant:", final_answer)
        save_message("assistant", final_answer)

        print()  # blank line for readability

if __name__ == "__main__":
    interactive_loop()
