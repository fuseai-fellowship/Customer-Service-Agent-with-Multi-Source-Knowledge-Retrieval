from agent_service.graph import build_graph
from langchain.schema import HumanMessage
from pydantic import BaseModel
from typing import Literal

graph = build_graph()

class ReviewDecision(BaseModel):
    decision: Literal["ok", "needs_more"]
    rationale: str = ""
    answer: str = ""
    todo: str = ""

def interactive_loop():
    print("Chat loop (type 'exit' to quit)\n")

    # Persisted compact chat history (human ↔ AI exchanges)
    chat_history = ""

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not user_input:
            continue

        # fresh state for this run
        state = {
            "messages": [],
            "summary": chat_history,  # inject prior conversation
            "tool_output": "",
            "review_decision": ReviewDecision(decision="needs_more")  # initial placeholder
        }

        # add current user message
        human_msg = HumanMessage(content=user_input)
        state["messages"].append(human_msg)
        state["summary"] += f"\nHuman: {user_input}"

        # invoke graph
        result = graph.invoke(state)

        # Extract final answer from result's review_decision
        review = result.get("review_decision")
        final_answer = review.answer if review else "(no answer)"

        # Print assistant's reply
        print("\nAssistant:", final_answer)

        # Update chat_history with human + AI turn only
        chat_history += f"\nHuman: {user_input}\nAI: {final_answer}"
        # Optional: trim history to last N chars/lines
        MAX_CHARS = 2000
        if len(chat_history) > MAX_CHARS:
            chat_history = chat_history[-MAX_CHARS:]

        print()  # blank line for readability

if __name__ == "__main__":
    interactive_loop()
