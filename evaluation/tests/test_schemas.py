import pytest
from pydantic import ValidationError

from nutriscan_eval.schemas import RecognitionResult


def test_valid_food_response_cleans_alternatives() -> None:
    result = RecognitionResult.model_validate(
        {
            "image_status": "food",
            "detected_foods": [
                {
                    "name": "  Pani   puri ",
                    "quantity": 6,
                    "unit": "piece",
                    "alternatives": ["golgappa", " Golgappa ", "Pani puri"],
                }
            ],
            "needs_user_review": True,
        }
    )
    assert result.detected_foods[0].name == "Pani puri"
    assert result.detected_foods[0].alternatives == ["golgappa"]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "image_status": "food",
            "detected_foods": [],
            "needs_user_review": True,
        },
        {
            "image_status": "unclear",
            "detected_foods": [{"name": "dal", "quantity": 1, "unit": "cup", "alternatives": []}],
            "needs_user_review": True,
        },
        {
            "image_status": "not_food",
            "detected_foods": [],
            "needs_user_review": False,
        },
    ],
)
def test_invalid_status_or_review_contract_is_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RecognitionResult.model_validate(payload)
