from app.agent.agent import run_agent

# deliberately needs evidence from two different products, to prove the agent
# actually decides to call a tool more than once on its own
QUESTION = (
    "Compare the MacBook Air (B08157248B) and the ASUS ROG Strix (B0BY2Y5T1J) "
    "on battery life and build quality. Which one seems better overall?"
)


def main() -> None:
    answer = run_agent(QUESTION)
    print(f"question: {QUESTION}\n")
    print(answer)


if __name__ == "__main__":
    main()
