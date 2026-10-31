import re
import unicodedata

_NON_WORD = re.compile(r"[^a-z0-9]+")

_ALIASES = {
    "chapati": "roti",
    "chapatis": "roti",
    "rotis": "roti",
    "gol gappa": "pani puri",
    "gol gappe": "pani puri",
    "golgappa": "pani puri",
    "golgappe": "pani puri",
    "cholebhature": "chole bhature",
    "kathiroll": "kathi roll",
    "paani puri": "pani puri",
    "panipuri": "pani puri",
    "pakoda": "pakora",
    "pakode": "pakora",
    "pakoras": "pakora",
    "kaathi roll": "kathi roll",
    "pavbhaji": "pav bhaji",
    "vadapav": "vada pav",
}


def normalize_food_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = _NON_WORD.sub(" ", normalized.casefold()).strip()
    normalized = " ".join(normalized.split())
    return _ALIASES.get(normalized, normalized)


def normalized_food_set(values: list[str]) -> set[str]:
    return {normalized for value in values if (normalized := normalize_food_name(value))}
