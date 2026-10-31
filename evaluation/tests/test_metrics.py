from nutriscan_eval.metrics import (
    aggregate_candidate,
    item_match_counts,
    percentile,
    top1_is_correct,
)
from nutriscan_eval.schemas import BenchmarkRecord, ProviderUsage, RecognitionResult


def _record(
    *,
    scope: str,
    expected: list[str],
    foods: list[tuple[str, list[str]]],
    status: str = "food",
    latency: float = 1.0,
    category: str = "everyday",
    with_portions: bool = False,
) -> BenchmarkRecord:
    prediction = RecognitionResult.model_validate(
        {
            "image_status": status,
            "detected_foods": [
                {
                    "name": name,
                    "quantity": 1 if with_portions else None,
                    "unit": "katori" if with_portions else "unknown",
                    "alternatives": alternatives,
                }
                for name, alternatives in foods
            ],
            "needs_user_review": True,
        }
    )
    return BenchmarkRecord(
        scope=scope,
        image_id="meal.jpg",
        benchmark_category=category,
        scenario="test",
        candidate_alias="primary",
        model="model",
        provider="deepinfra",
        expected_foods=expected,
        prediction=prediction,
        schema_valid=True,
        latency_seconds=latency,
        usage=ProviderUsage(),
        estimated_cost_usd="0.001",
        run_timestamp="2026-10-26T00:00:00+00:00",
    )


def test_top1_accepts_a_synonymous_alternative() -> None:
    record = _record(scope="public", expected=["pani puri"], foods=[("snack", ["golgappa"])])
    assert top1_is_correct(record)


def test_mixed_item_counts_do_not_count_alternatives_as_extra_predictions() -> None:
    record = _record(
        scope="private",
        expected=["dal", "rice", "roti"],
        foods=[("lentil curry", ["dal"]), ("rice", []), ("salad", [])],
    )
    assert item_match_counts(record) == (2, 1, 1)


def test_mixed_item_matching_finds_maximum_non_overlapping_assignment() -> None:
    record = _record(
        scope="private",
        expected=["dal", "lentil curry"],
        foods=[("stew", ["dal", "lentil curry"]), ("dal", [])],
    )
    assert item_match_counts(record) == (2, 0, 0)


def test_aggregate_keeps_public_and_private_metrics_separate() -> None:
    public = _record(scope="public", expected=["roti"], foods=[("chapati", [])], latency=1)
    mixed = _record(
        scope="private", expected=["dal", "rice"], foods=[("dal", []), ("rice", [])], latency=3
    )
    control = _record(scope="private", expected=[], foods=[], status="unclear", latency=2)
    summary = aggregate_candidate([public, mixed, control])
    assert summary.public_top1_accuracy == 1
    assert summary.private_item_f1 == 1
    assert summary.private_mixed_f1 == 1
    assert summary.unclear_control_pass_rate == 1
    assert summary.private_p95_latency_seconds == 3


def test_portion_coverage_counts_only_correctly_matched_private_foods() -> None:
    complete = _record(
        scope="private",
        expected=["dal", "rice"],
        foods=[("dal", []), ("rice", []), ("salad", [])],
        with_portions=True,
    )
    incomplete = _record(
        scope="private",
        expected=["roti"],
        foods=[("chapati", [])],
    )
    summary = aggregate_candidate([complete, incomplete])
    assert summary.private_portion_matches == 3
    assert summary.private_portion_complete_rate == 2 / 3


def test_nearest_rank_percentile() -> None:
    assert percentile(range(1, 101), 0.95) == 95
