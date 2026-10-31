import csv
import re
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

PUBLIC_DATASET_ID = "bharat-raghunathan/indian-foods-dataset"
PUBLIC_DATASET_REVISION = "ef509a8b4bfd46b76530ad329f81586faf904aad"
PUBLIC_SPLIT = "test"
PUBLIC_CLASS_COUNT = 15
PUBLIC_PER_CLASS = 5
PRIVATE_IMAGE_COUNT = 30
PRIVATE_CATEGORY_COUNTS = {
    "everyday": 12,
    "protein": 8,
    "produce": 5,
    "indulgent": 2,
    "control": 3,
}


@dataclass(frozen=True, slots=True)
class ManifestItem:
    filename: str
    expected_foods: list[str]
    scenario: str
    benchmark_category: str = ""
    portion_notes: str = ""

    def image_path(self, image_root: Path) -> Path:
        root = image_root.resolve()
        candidate = (root / self.filename).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(f"Manifest path escapes image directory: {self.filename}")
        if not candidate.is_file():
            raise ValueError(f"Image does not exist: {self.filename}")
        return candidate


def select_balanced(
    examples: Iterable[tuple[str, Any]], *, per_class: int = PUBLIC_PER_CLASS
) -> dict[str, list[Any]]:
    selected: dict[str, list[Any]] = defaultdict(list)
    for label, payload in examples:
        if len(selected[label]) < per_class:
            selected[label].append(payload)
    return dict(selected)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "class"


def _extract_label_name(example: dict[str, Any], label_feature: Any) -> str:
    raw_label = example["label"]
    if hasattr(label_feature, "int2str"):
        return str(label_feature.int2str(raw_label))
    return str(raw_label)


def _stream_examples() -> tuple[Iterator[dict[str, Any]], Any]:
    from datasets import load_dataset

    dataset = load_dataset(
        PUBLIC_DATASET_ID,
        revision=PUBLIC_DATASET_REVISION,
        split=PUBLIC_SPLIT,
        streaming=True,
    )
    label_feature = dataset.features["label"]
    return iter(dataset), label_feature


def prepare_public_dataset(output: Path, *, per_class: int = PUBLIC_PER_CLASS) -> Path:
    if per_class != PUBLIC_PER_CLASS:
        raise ValueError("The public diagnostic requires exactly five examples per class")
    image_dir = output / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    stream, label_feature = _stream_examples()
    selected: dict[str, list[Image.Image]] = defaultdict(list)
    for example in stream:
        label = _extract_label_name(example, label_feature)
        if len(selected[label]) < per_class:
            selected[label].append(example["image"].copy())
        if len(selected) == PUBLIC_CLASS_COUNT and all(
            len(items) == per_class for items in selected.values()
        ):
            break
    if len(selected) != PUBLIC_CLASS_COUNT or any(
        len(items) != per_class for items in selected.values()
    ):
        counts = {label: len(items) for label, items in selected.items()}
        raise RuntimeError(f"Could not collect the required balanced public set: {counts}")

    manifest_path = output / "labels.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "filename",
                "expected_foods",
                "benchmark_category",
                "scenario",
                "portion_notes",
            ],
        )
        writer.writeheader()
        for label in sorted(selected):
            for index, image in enumerate(selected[label], start=1):
                filename = f"{_slug(label)}-{index:02d}.jpg"
                image.convert("RGB").save(image_dir / filename, "JPEG", quality=95)
                writer.writerow(
                    {
                        "filename": filename,
                        "expected_foods": label,
                        "benchmark_category": "public_diagnostic",
                        "scenario": "public_single_dish",
                        "portion_notes": "",
                    }
                )
    return manifest_path


def load_manifest(path: Path, image_root: Path) -> list[ManifestItem]:
    required = {"filename", "expected_foods", "scenario", "portion_notes"}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest is missing columns: {', '.join(sorted(missing))}")
        items = [
            ManifestItem(
                filename=row["filename"].strip(),
                expected_foods=[
                    food.strip() for food in row["expected_foods"].split("|") if food.strip()
                ],
                scenario=row["scenario"].strip(),
                benchmark_category=row.get("benchmark_category", "").strip(),
                portion_notes=row["portion_notes"].strip(),
            )
            for row in reader
        ]
    filenames = [item.filename for item in items]
    if any(not filename for filename in filenames):
        raise ValueError("Manifest filenames cannot be blank")
    if len(filenames) != len(set(filenames)):
        raise ValueError("Manifest filenames must be unique")
    if any(not item.scenario for item in items):
        raise ValueError("Every manifest row needs a scenario")
    for item in items:
        item.image_path(image_root)
    return items


def validate_public_manifest(items: list[ManifestItem]) -> None:
    if len(items) != PUBLIC_CLASS_COUNT * PUBLIC_PER_CLASS:
        raise ValueError("Public manifest must contain exactly 75 rows")
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        if len(item.expected_foods) != 1:
            raise ValueError("Every public example must have exactly one expected food")
        counts[item.expected_foods[0]] += 1
    if len(counts) != PUBLIC_CLASS_COUNT or set(counts.values()) != {PUBLIC_PER_CLASS}:
        raise ValueError("Public manifest must contain five examples from each of 15 classes")


def validate_private_manifest(items: list[ManifestItem]) -> None:
    if len(items) != PRIVATE_IMAGE_COUNT:
        raise ValueError("Private benchmark must contain exactly 30 images")

    category_counts: dict[str, int] = defaultdict(int)
    for item in items:
        category_counts[item.benchmark_category] += 1
    if dict(category_counts) != PRIVATE_CATEGORY_COUNTS:
        raise ValueError(
            "Private benchmark category counts must be "
            "12 everyday, 8 protein, 5 produce, 2 indulgent, and 3 control"
        )

    controls = [item for item in items if item.benchmark_category == "control"]
    food_items = [item for item in items if item.benchmark_category != "control"]
    if any(item.expected_foods for item in controls):
        raise ValueError("Control images cannot have expected foods")
    if any(not item.expected_foods for item in food_items):
        raise ValueError("Every non-control image needs at least one expected food")
    if any(not item.portion_notes for item in food_items):
        raise ValueError("Every non-control image needs human-reviewed portion notes")
    if sum(len(item.expected_foods) >= 2 for item in items) < 10:
        raise ValueError("Private manifest must contain at least 10 mixed meals")

    scenarios = " ".join(item.scenario.casefold().replace("-", "_") for item in items)
    required_scenarios = {
        "home": "home",
        "restaurant": "restaurant",
        "thali": "thali",
        "takeaway": "takeaway",
        "low-light": "low_light",
        "occlusion": "occlusion",
        "visually confusing pair": "confusing_pair",
    }
    missing = [label for label, marker in required_scenarios.items() if marker not in scenarios]
    if missing:
        raise ValueError(f"Private scenarios are missing: {', '.join(missing)}")
