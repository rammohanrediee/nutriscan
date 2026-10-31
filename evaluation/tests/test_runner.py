import json
from decimal import Decimal
from pathlib import Path

import pytest
from PIL import Image

from nutriscan_eval.candidates import CANDIDATES
from nutriscan_eval.costs import BudgetLedger
from nutriscan_eval.dataset import ManifestItem
from nutriscan_eval.provider import ProviderFailure, ProviderObservation
from nutriscan_eval.runner import evaluate_item, run_full_benchmark
from nutriscan_eval.schemas import ProviderUsage, RecognitionResult


def _image(path: Path) -> None:
    Image.new("RGB", (8, 8), "white").save(path, "JPEG")


def _result() -> RecognitionResult:
    return RecognitionResult.model_validate(
        {
            "image_status": "food",
            "detected_foods": [
                {
                    "name": "Dal",
                    "quantity": 1,
                    "unit": "katori",
                    "alternatives": ["lentil curry"],
                }
            ],
            "needs_user_review": True,
        }
    )


class SuccessfulProvider:
    async def recognize(self, *_: object) -> ProviderObservation:
        return ProviderObservation(
            result=_result(),
            latency_seconds=0.5,
            usage=ProviderUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120),
            response_id="response-1",
            system_fingerprint=None,
            nutrition_leak=False,
        )


class FailingProvider:
    async def recognize(self, *_: object) -> ProviderObservation:
        raise ProviderFailure(
            "INVALID_SCHEMA",
            "invalid response",
            latency_seconds=0.25,
            nutrition_leak=True,
            usage=ProviderUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )


@pytest.mark.asyncio
async def test_evaluate_item_records_normalized_success(tmp_path: Path) -> None:
    image = tmp_path / "meal.jpg"
    _image(image)
    ledger = BudgetLedger(cap_usd=Decimal("1"))
    record = await evaluate_item(
        SuccessfulProvider(),
        ledger,
        CANDIDATES["primary"],
        ManifestItem(image.name, ["dal"], "home", "everyday", "one bowl"),
        tmp_path,
        scope="private",
    )
    assert record.schema_valid
    assert record.benchmark_category == "everyday"
    assert record.normalized_foods == ["dal"]
    assert Decimal(record.estimated_cost_usd) > 0


@pytest.mark.asyncio
async def test_evaluate_item_redacts_provider_failure(tmp_path: Path) -> None:
    image = tmp_path / "meal.jpg"
    _image(image)
    record = await evaluate_item(
        FailingProvider(),
        BudgetLedger(cap_usd=Decimal("1")),
        CANDIDATES["primary"],
        ManifestItem(image.name, ["dal"], "home", "everyday", "one bowl"),
        tmp_path,
        scope="private",
    )
    assert not record.schema_valid
    assert record.prediction is None
    assert record.error_code == "INVALID_SCHEMA"
    assert record.nutrition_leak


@pytest.mark.asyncio
async def test_full_benchmark_writes_diagnostics_and_gate_summary(tmp_path: Path) -> None:
    public_root = tmp_path / "public"
    private_root = tmp_path / "private"
    public_root.mkdir()
    private_root.mkdir()
    _image(public_root / "public.jpg")
    _image(private_root / "private.jpg")
    output = tmp_path / "results"

    winner, summaries = await run_full_benchmark(
        SuccessfulProvider(),
        BudgetLedger(cap_usd=Decimal("1")),
        [CANDIDATES["primary"]],
        [ManifestItem("public.jpg", ["dal"], "public_single", "public_diagnostic")],
        public_root,
        [ManifestItem("private.jpg", ["dal"], "home", "everyday", "one bowl")],
        private_root,
        output,
    )

    assert winner is None
    assert summaries["primary"].public_top1_accuracy == 1
    assert summaries["primary"].private_item_f1 == 1
    payload = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert payload["winner"] is None
    assert payload["excluded_after_smoke"] == []
    assert (output / "primary-public.jsonl").is_file()
    assert (output / "primary-private.jsonl").is_file()
