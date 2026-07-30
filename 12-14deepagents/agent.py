import os
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    model_name="MiniMax-M3",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY"),
)

backend = LocalShellBackend("./", virtual_mode=True)

agent = create_deep_agent(
    model=model,
    backend=backend,
    skills=["./my-project/skills/"],
)


def main() -> None:
    """Run an interactive REPL session with the deep agent."""
    messages: list[dict] = []
    print("Deep agent ready. Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break

        messages.append({"role": "user", "content": user_input})
        result = agent.invoke({"messages": messages})
        reply = result["messages"][-1]
        messages.append({"role": "assistant", "content": reply.content})
        print(f"Agent> {reply.content}\n")


if __name__ == "__main__":
    main()