from app.db.session import SessionLocal
from app.generation.answer import generate_answer
from app.retrieval.dense import retrieve

QUESTION = "does the battery drain fast"


def main() -> None:
    session = SessionLocal()

    # same retrieve() from the dense retrieval step, feeding straight into generation
    results = retrieve(session, QUESTION, k=5)
    answer = generate_answer(QUESTION, results)

    print(f"question: {QUESTION}\n")
    print(answer)

    session.close()


if __name__ == "__main__":
    main()
