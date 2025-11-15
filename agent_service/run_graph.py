from agent_service.graph import build_graph
from langchain.schema import HumanMessage


graph = build_graph()


def interactive_loop():
    print("Chat loop (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not user_input:
            continue

        # fresh state for this run
        state = {
            "query": user_input,
            "chat_history": [],
            "subagent_outputs": [] 
        }
     
        # invoke graph
        result = graph.invoke(state)
        final_answer = result["final_response"]

        # Print assistant's reply
        print("\nAssistant:", final_answer)

        print()  # blank line for readability

if __name__ == "__main__":
    interactive_loop()
