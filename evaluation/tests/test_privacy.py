import base64
import io
from pathlib import Path

from PIL import Image

from nutriscan_eval.privacy import (
    contains_nutrition_language,
    image_to_data_url,
    redact_path,
    safe_error,
)


def test_image_is_resized_and_encoded_in_memory(tmp_path: Path) -> None:
    image_path = tmp_path / "private-meal.png"
    Image.new("RGB", (2000, 1000), "red").save(image_path)
    data_url = image_to_data_url(image_path, max_edge=100)
    assert data_url.startswith("data:image/jpeg;base64,")
    decoded = base64.b64decode(data_url.split(",", 1)[1])
    with Image.open(io.BytesIO(decoded)) as image:
        assert image.format == "JPEG"
        assert image.size == (100, 50)
        assert not image.getexif()


def test_private_paths_and_tokens_are_redacted(tmp_path: Path) -> None:
    private = tmp_path / "private meal" / "images"
    private.mkdir(parents=True)
    image = private / "meal.jpg"
    image.touch()
    assert redact_path(image, tmp_path / "private meal") == "<private>/meal.jpg"
    message = safe_error(f"failed at '{image}' with hf_abcdefghijklmnop")
    assert str(tmp_path) not in message
    assert "hf_abcdefghijklmnop" not in message


def test_nutrition_language_detection() -> None:
    assert contains_nutrition_language("This has 250 kcal")
    assert not contains_nutrition_language("one katori of dal")
