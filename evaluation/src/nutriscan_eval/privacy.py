import base64
import io
import re
from pathlib import Path

from PIL import Image, ImageOps

MAX_IMAGE_EDGE = 1536
JPEG_QUALITY = 85
_TOKEN_PATTERN = re.compile(r"hf_[A-Za-z0-9]{8,}")
_QUOTED_ABSOLUTE_PATH_PATTERN = re.compile(r"(?P<quote>['\"])/.+?(?P=quote)")
_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<![\w.])/(?:[^\s/:]+/)+[^\s:]*")
_NUTRITION_PATTERN = re.compile(
    r"\b(?:calories?|kcal|kilocalories?|protein|carbohydrates?|carbs?|fat|fibre|fiber|sodium|"
    r"cholesterol|macros?|nutrients?|nutrition)\b",
    re.IGNORECASE,
)


def image_to_data_url(path: Path, *, max_edge: int = MAX_IMAGE_EDGE) -> str:
    """Normalize an image in memory and return a metadata-free JPEG data URL."""
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def redact_path(path: Path, private_root: Path | None = None) -> str:
    resolved = path.resolve()
    if private_root is not None and resolved.is_relative_to(private_root.resolve()):
        return f"<private>/{resolved.name}"
    return resolved.name


def safe_error(value: object) -> str:
    message = _TOKEN_PATTERN.sub("<redacted-token>", str(value))
    message = _QUOTED_ABSOLUTE_PATH_PATTERN.sub("'<redacted-path>'", message)
    return _ABSOLUTE_PATH_PATTERN.sub("<redacted-path>", message)[:500]


def contains_nutrition_language(value: str) -> bool:
    return bool(_NUTRITION_PATTERN.search(value))
