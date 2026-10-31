import csv
from pathlib import Path

import pytest

from nutriscan_eval.dataset import (
    load_manifest,
    select_balanced,
    validate_private_manifest,
    validate_public_manifest,
)


def test_balanced_selection_is_deterministic() -> None:
    examples = [("b", 1), ("a", 2), ("a", 3), ("a", 4), ("b", 5), ("b", 6)]
    assert select_balanced(examples, per_class=2) == {"b": [1, 5], "a": [2, 3]}


def _write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
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
        writer.writerows(rows)


def test_public_manifest_requires_five_of_fifteen_classes(tmp_path: Path) -> None:
    rows = []
    for class_index in range(15):
        for image_index in range(5):
            filename = f"{class_index}-{image_index}.jpg"
            (tmp_path / filename).touch()
            rows.append(
                {
                    "filename": filename,
                    "expected_foods": f"dish {class_index}",
                    "benchmark_category": "public_diagnostic",
                    "scenario": "public_single_dish",
                    "portion_notes": "",
                }
            )
    manifest = tmp_path / "labels.csv"
    _write_manifest(manifest, rows)
    items = load_manifest(manifest, tmp_path)
    validate_public_manifest(items)


def test_private_manifest_requirements_are_enforced(tmp_path: Path) -> None:
    category_by_index = [
        *(["everyday"] * 12),
        *(["protein"] * 8),
        *(["produce"] * 5),
        *(["indulgent"] * 2),
        *(["control"] * 3),
    ]
    scenario_by_index = [
        "home|thali|mixed",
        "restaurant|mixed",
        "takeaway|mixed",
        "low_light|mixed",
        "occlusion|mixed",
        "confusing_pair|mixed",
    ]
    rows = []
    for index in range(30):
        filename = f"private-{index}.jpg"
        (tmp_path / filename).touch()
        if category_by_index[index] == "control":
            foods = ""
            scenario = "unclear_control"
            portion_notes = "Not a reliably identifiable food image"
        elif index < 10:
            foods = "dal|rice"
            scenario = scenario_by_index[index % len(scenario_by_index)]
            portion_notes = "One serving of each visible food"
        else:
            foods = "idli"
            scenario = scenario_by_index[index % len(scenario_by_index)]
            portion_notes = "Two visible pieces"
        rows.append(
            {
                "filename": filename,
                "expected_foods": foods,
                "benchmark_category": category_by_index[index],
                "scenario": scenario,
                "portion_notes": portion_notes,
            }
        )
    manifest = tmp_path / "labels.csv"
    _write_manifest(manifest, rows)
    validate_private_manifest(load_manifest(manifest, tmp_path))


def test_private_manifest_rejects_old_flexible_size(tmp_path: Path) -> None:
    rows = []
    for index in range(20):
        filename = f"private-{index}.jpg"
        (tmp_path / filename).touch()
        rows.append(
            {
                "filename": filename,
                "expected_foods": "dal|rice",
                "benchmark_category": "everyday",
                "scenario": "home|mixed",
                "portion_notes": "One bowl of each",
            }
        )
    manifest = tmp_path / "labels.csv"
    _write_manifest(manifest, rows)
    with pytest.raises(ValueError, match="exactly 30"):
        validate_private_manifest(load_manifest(manifest, tmp_path))


def test_manifest_rejects_parent_path_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.jpg"
    outside.touch()
    manifest = tmp_path / "labels.csv"
    _write_manifest(
        manifest,
        [
            {
                "filename": "../outside.jpg",
                "expected_foods": "dal",
                "benchmark_category": "everyday",
                "scenario": "test",
                "portion_notes": "",
            }
        ],
    )
    with pytest.raises(ValueError, match="escapes"):
        load_manifest(manifest, tmp_path)
