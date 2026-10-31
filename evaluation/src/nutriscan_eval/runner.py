import json
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from .candidates import Candidate
from .costs import BudgetLedger, estimate_cost
from .dataset import ManifestItem
from .metrics import CandidateSummary, aggregate_candidate
from .normalization import normalize_food_name
from .privacy import image_to_data_url
from .provider import ProviderFailure, VisionProvider
from .schemas import BenchmarkRecord
from .selection import select_winner


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_records(path: Path, records: list[BenchmarkRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(record.model_dump_json() + "\n")


async def evaluate_item(
    provider: VisionProvider,
    ledger: BudgetLedger,
    candidate: Candidate,
    item: ManifestItem,
    image_root: Path,
    *,
    scope: str,
) -> BenchmarkRecord:
    ledger.reserve_request()
    try:
        observation = await provider.recognize(
            candidate, image_to_data_url(item.image_path(image_root))
        )
    except ProviderFailure as error:
        actual_cost = estimate_cost(error.usage, candidate)
        if actual_cost == 0:
            actual_cost = ledger.reserve_per_request_usd
        ledger.commit_request(actual_cost)
        return BenchmarkRecord(
            scope=scope,
            image_id=Path(item.filename).name,
            benchmark_category=item.benchmark_category,
            scenario=item.scenario,
            candidate_alias=candidate.alias,
            model=candidate.model,
            provider=candidate.provider,
            expected_foods=item.expected_foods,
            prediction=None,
            normalized_foods=[],
            schema_valid=False,
            latency_seconds=error.latency_seconds,
            usage=error.usage,
            estimated_cost_usd=str(actual_cost),
            error_code=error.code,
            nutrition_leak=error.nutrition_leak,
            run_timestamp=_timestamp(),
        )
    except Exception:
        ledger.release_request()
        raise

    actual_cost = estimate_cost(observation.usage, candidate)
    ledger.commit_request(actual_cost)
    return BenchmarkRecord(
        scope=scope,
        image_id=Path(item.filename).name,
        benchmark_category=item.benchmark_category,
        scenario=item.scenario,
        candidate_alias=candidate.alias,
        model=candidate.model,
        provider=candidate.provider,
        expected_foods=item.expected_foods,
        prediction=observation.result,
        normalized_foods=[
            normalize_food_name(food.name) for food in observation.result.detected_foods
        ],
        schema_valid=True,
        latency_seconds=observation.latency_seconds,
        usage=observation.usage,
        estimated_cost_usd=str(actual_cost),
        nutrition_leak=observation.nutrition_leak,
        run_timestamp=_timestamp(),
    )


async def run_smoke_tests(
    provider: VisionProvider,
    ledger: BudgetLedger,
    candidates: list[Candidate],
    image: Path,
    output: Path,
) -> dict[str, BenchmarkRecord]:
    item = ManifestItem(
        filename=image.name,
        expected_foods=[],
        scenario="transport_smoke",
        benchmark_category="smoke",
    )
    records: dict[str, BenchmarkRecord] = {}
    for candidate in candidates:
        record = await evaluate_item(provider, ledger, candidate, item, image.parent, scope="smoke")
        records[candidate.alias] = record
    _write_records(output / "smoke.jsonl", list(records.values()))
    return records


async def run_full_benchmark(
    provider: VisionProvider,
    ledger: BudgetLedger,
    candidates: list[Candidate],
    public_items: list[ManifestItem],
    public_images: Path,
    private_items: list[ManifestItem],
    private_images: Path,
    output: Path,
) -> tuple[str | None, dict[str, CandidateSummary]]:
    output.mkdir(parents=True, exist_ok=True)
    preflight = await run_smoke_tests(
        provider, ledger, candidates, private_items[0].image_path(private_images), output
    )
    eligible = [candidate for candidate in candidates if preflight[candidate.alias].schema_valid]

    all_records: dict[str, list[BenchmarkRecord]] = defaultdict(list)
    for candidate in eligible:
        for scope, items, image_root in (
            ("public", public_items, public_images),
            ("private", private_items, private_images),
        ):
            scope_records: list[BenchmarkRecord] = []
            for item in items:
                record = await evaluate_item(
                    provider, ledger, candidate, item, image_root, scope=scope
                )
                scope_records.append(record)
                all_records[candidate.alias].append(record)
            _write_records(output / f"{candidate.alias}-{scope}.jsonl", scope_records)

    summaries = {
        alias: aggregate_candidate(records) for alias, records in all_records.items() if records
    }
    winner, decisions = select_winner(summaries)
    summary_payload = {
        "benchmark_timestamp": _timestamp(),
        "budget_cap_usd": str(ledger.cap_usd),
        "estimated_spend_usd": str(ledger.spent_usd.quantize(Decimal("0.00000001"))),
        "winner": winner,
        "summaries": {alias: summary.as_dict() for alias, summary in summaries.items()},
        "gate_decisions": [
            {
                "candidate_alias": decision.candidate_alias,
                "passed": decision.passed,
                "failures": list(decision.failures),
            }
            for decision in decisions
        ],
        "excluded_after_smoke": [
            alias for alias, record in preflight.items() if not record.schema_valid
        ],
    }
    (output / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return winner, summaries
