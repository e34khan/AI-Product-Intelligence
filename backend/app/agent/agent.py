from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.agent.tools import get_aspect_summary, retrieve_reviews

load_dotenv()

client = genai.Client()

MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are a product research assistant. You have tools to look up real "
    "customer review evidence and aspect-based sentiment summaries for "
    "specific products, identified by their ASIN. Decide which tools you "
    "need, call them, then answer the user's question using only the "
    "evidence they return. If comparing products, call the tools "
    "separately for each product's ASIN before synthesizing a comparison."
)

# schemas only, not real functions, so this never triggers the sdk's
# automatic function calling. we want to run the loop ourselves
TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_reviews",
            description="Retrieve relevant customer review excerpts for one product and a specific question.",
            parameters={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "The product's ASIN"},
                    "question": {"type": "string", "description": "What to look for in the reviews"},
                },
                "required": ["product_id", "question"],
            },
        ),
        types.FunctionDeclaration(
            name="get_aspect_summary",
            description="Get aggregated aspect-based sentiment counts (battery, display, keyboard, etc) for one product.",
            parameters={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "The product's ASIN"},
                },
                "required": ["product_id"],
            },
        ),
    ])
]

# maps a tool name the model might request back to the real python function
AVAILABLE_FUNCTIONS = {
    "retrieve_reviews": retrieve_reviews,
    "get_aspect_summary": get_aspect_summary,
}


def run_agent(question: str, max_turns: int = 6) -> str:
    history = [types.Content(role="user", parts=[types.Part(text=question)])]

    for _ in range(max_turns):
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=TOOLS,
            ),
        )

        candidate = response.candidates[0]
        history.append(candidate.content)  # the model's turn, including any tool requests

        function_calls = [part.function_call for part in candidate.content.parts if part.function_call]

        if not function_calls:
            return response.text  # no more tools requested, this is the final answer

        function_response_parts = []
        for call in function_calls:
            print(f"[agent] calling {call.name}({dict(call.args)})")
            function = AVAILABLE_FUNCTIONS[call.name]
            result = function(**call.args)
            function_response_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )

        # feed the real results back in as the next turn, then loop again
        history.append(types.Content(role="user", parts=function_response_parts))

    return "Agent did not reach a final answer within the turn limit."
