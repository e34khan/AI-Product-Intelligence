from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.db.models import Chunk

load_dotenv()  # makes sure GEMINI_API_KEY is loaded even if this module gets imported first

client = genai.Client()  # reads GEMINI_API_KEY from the environment automatically

MODEL_NAME = "gemini-3.6-flash"  # fast and cheap, good enough for grounded QA over a few chunks

SYSTEM_PROMPT = (
    "You are answering questions about a product using only the customer review "
    "excerpts provided below. Only make claims the evidence actually supports. "
    "Cite each claim using the bracket number of the excerpt it came from, like [1]. "
    "If the evidence does not cover the question, say so instead of guessing."
)


def build_evidence_block(results: list[tuple[Chunk, float]]) -> str:
    # numbering starts at 1 so the model can cite chunks back as [1], [2], etc
    lines = [f"[{i}] {chunk.text}" for i, (chunk, _distance) in enumerate(results, start=1)]
    return "\n\n".join(lines)


def generate_answer(question: str, results: list[tuple[Chunk, float]]) -> str:
    evidence = build_evidence_block(results)
    prompt = f"Evidence:\n{evidence}\n\nQuestion: {question}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )

    return response.text
