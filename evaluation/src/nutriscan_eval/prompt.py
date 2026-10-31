from typing import Any

from .schemas import RecognitionResult

SYSTEM_PROMPT = """You are a cautious visual food recognizer for Indian meals.
Identify only food visibly supported by the image. A plate may contain multiple foods. Use familiar,
specific dish names when justified and short generic names when it is not. Suggest rough visible
portions using only the allowed units. Put plausible visual alternatives in alternatives.

Never calculate, estimate, mention, or return calories, macros, nutrients, health advice, catalog
IDs, or ingredient quantities. If the image is not food, return not_food and no foods. If it is too
ambiguous to identify responsibly, return unclear and no foods. Never guess to fill the list.
needs_user_review must always be true. Return only JSON matching the supplied schema."""

USER_PROMPT = "Inspect this image and return a Recognition Suggestion for the visible food."


def strict_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "RecognitionResult",
            "strict": True,
            "schema": RecognitionResult.model_json_schema(),
        },
    }


def messages_for_image(data_url: str) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": USER_PROMPT},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        },
    ]
