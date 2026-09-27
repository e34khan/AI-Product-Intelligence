import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

MODEL_NAME = "gemini-3.5-flash-lite"  # 500/day free tier vs gemini-3.6-flash's 20/day

# keeps us comfortably under the per-minute limit too, not just the daily one
SECONDS_BETWEEN_CALLS = 3

# a fixed vocabulary, not open-ended, so aggregation later doesn't fragment
# into near-duplicate labels like "battery" vs "battery life"
ASPECTS = {
    "battery": "battery life, charging, how long it lasts",
    "display": "screen quality, resolution, brightness, touchscreen",
    "keyboard": "keyboard feel, key issues, backlighting",
    "build_quality": "physical condition, durability, scratches, dents, materials",
    "thermal_fan_noise": "overheating, fan noise, running hot",
    "performance_speed": "processing speed, boot time, responsiveness, lag",
    "value_price": "whether it is worth the price, good deal or not",
    "portability_weight": "how light or heavy, how portable the laptop is",
    "customer_service": "seller responsiveness, returns, support experience",
    "software_reliability": "crashes, freezes, glitches, OS issues",
}


# pydantic models here double as the response_schema handed to the LLM api,
# which is what makes it return real structured json instead of free text
# we would otherwise have to parse ourselves and hope it stays consistent
class AspectMention(BaseModel):
    aspect: str
    sentiment: str  # positive, negative, neutral, or mixed
    quote: str  # the exact snippet from the review backing this judgment


class ExtractionResult(BaseModel):
    mentions: list[AspectMention]


def build_system_prompt() -> str:
    aspect_lines = "\n".join(f"- {name}: {description}" for name, description in ASPECTS.items())
    return (
        "You are extracting aspect-based sentiment from a single product review.\n"
        "Only use these aspect categories, exactly as spelled:\n"
        f"{aspect_lines}\n\n"
        "For each aspect actually discussed in the review, report its sentiment "
        "(positive, negative, neutral, or mixed) and a short exact quote from the "
        "review that supports that judgment. If a sentence discusses multiple "
        "aspects, attribute sentiment to each one correctly rather than lumping "
        "them together. If the review does not discuss a given aspect, do not "
        "include it. If it discusses none of these aspects, return an empty list."
    )


def extract_aspects(review_text: str, max_retries: int = 4) -> list[AspectMention]:
    time.sleep(SECONDS_BETWEEN_CALLS)  # stay under the free tier's rate limit

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=review_text,
                config=types.GenerateContentConfig(
                    system_instruction=build_system_prompt(),
                    response_mime_type="application/json",
                    response_schema=ExtractionResult,
                ),
            )
            result = ExtractionResult.model_validate_json(response.text)
            return result.mentions
        except APIError:
            # covers both transient server overload and rate-limit rejections,
            # neither of which is a bug in our own code, so back off and retry
            if attempt == max_retries - 1:
                raise
            time.sleep(2**attempt)  # 1s, 2s, 4s, 8s between attempts
