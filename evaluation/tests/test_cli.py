import csv
from argparse import Namespace
from pathlib import Path

import pytest

from nutriscan_eval import cli


def _valid_private_manifest(root: Path) -> Path:
    category_by_index = [
        *(["everyday"] * 12),
        *(["protein"] * 8),
        *(["produce"] * 5),
        *(["indulgent"] * 2),
        *(["control"] * 3),
    ]
    scenarios = [
        "home|thali|mixed",
        "restaurant|mixed",
        "takeaway|mixed",
        "low_light|mixed",
        "occlusion|mixed",
        "confusing_pair|mixed",
    ]
    manifest = root / "labels.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
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
        for index, category in enumerate(category_by_index):
            filename = f"meal-{index}.jpg"
            (root / filename).touch()
            is_control = category == "control"
            writer.writerow(
                {
                    "filename": filename,
                    "expected_foods": "" if is_control else "dal|rice" if index < 10 else "dal",
                    "benchmark_category": category,
                    "scenario": "unclear_control" if is_control else scenarios[index % 6],
                    "portion_notes": "not food" if is_control else "one bowl",
                }
            )
    return manifest


def test_aliases_validate_candidate_names() -> None:
    assert cli._aliases("primary, challenger") == ["primary", "challenger"]
    with pytest.raises(ValueError, match="Unknown candidate"):
        cli._aliases("missing")


def test_live_token_must_be_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(SystemExit, match="HF_TOKEN is not set"):
        cli._live_token()
    monkeypatch.setenv("HF_TOKEN", "fixture-token")
    assert cli._live_token() == "fixture-token"


def test_current_terms_require_fresh_snapshot_and_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "PRICE_SNAPSHOT_DATE", "1900-01-01")
    with pytest.raises(SystemExit, match="snapshot is stale"):
        cli._require_current_terms(Namespace(confirm_current_terms=True))

    monkeypatch.setattr(cli, "PRICE_SNAPSHOT_DATE", cli.date.today().isoformat())
    with pytest.raises(SystemExit, match="confirm-current-terms"):
        cli._require_current_terms(Namespace(confirm_current_terms=False))
    cli._require_current_terms(Namespace(confirm_current_terms=True))


def test_validate_private_command_accepts_new_product_distribution(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = _valid_private_manifest(tmp_path)
    exit_code = cli.main(
        [
            "validate-private",
            "--images",
            str(tmp_path),
            "--manifest",
            str(manifest),
        ]
    )
    assert exit_code == 0
    assert "Private manifest is valid: 30 images" in capsys.readouterr().out


def test_validate_private_command_reports_bad_manifest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = tmp_path / "labels.csv"
    manifest.write_text("filename,expected_foods,scenario,portion_notes\n", encoding="utf-8")
    exit_code = cli.main(
        [
            "validate-private",
            "--images",
            str(tmp_path),
            "--manifest",
            str(manifest),
        ]
    )
    assert exit_code == 1
    assert "exactly 30 images" in capsys.readouterr().err
