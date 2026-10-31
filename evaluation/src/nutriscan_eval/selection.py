from dataclasses import dataclass

from .dataset import PRIVATE_CATEGORY_COUNTS, PRIVATE_IMAGE_COUNT
from .metrics import CandidateSummary


@dataclass(frozen=True, slots=True)
class GateDecision:
    candidate_alias: str
    passed: bool
    failures: tuple[str, ...]


def evaluate_gate(summary: CandidateSummary) -> GateDecision:
    failures: list[str] = []
    checks = (
        (
            summary.private_examples == PRIVATE_IMAGE_COUNT,
            "private benchmark must contain 30 images",
        ),
        (
            summary.private_category_counts == PRIVATE_CATEGORY_COUNTS,
            "private benchmark category distribution is invalid",
        ),
        (summary.private_schema_valid_rate == 1.0, "private schema validity must be 100%"),
        (summary.private_item_f1 >= 0.75, "private item-level F1 is below 0.75"),
        (summary.private_mixed_examples >= 10, "private benchmark needs at least 10 mixed meals"),
        (summary.private_mixed_f1 >= 0.75, "private mixed-meal F1 is below 0.75"),
        (
            summary.private_portion_complete_rate >= 0.80,
            "usable portion coverage is below 80%",
        ),
        (summary.private_p95_latency_seconds <= 10.0, "private p95 latency exceeds 10 seconds"),
        (summary.private_mean_cost_usd <= 0.01, "private mean cost exceeds US$0.01 per scan"),
        (summary.private_nutrition_leaks == 0, "model generated nutrition language"),
        (summary.unclear_controls == 3, "private benchmark must contain exactly 3 controls"),
        (summary.unclear_control_pass_rate == 1.0, "an unclear/non-food control failed"),
    )
    failures.extend(message for passed, message in checks if not passed)
    return GateDecision(summary.candidate_alias, not failures, tuple(failures))


def select_winner(summaries: dict[str, CandidateSummary]) -> tuple[str | None, list[GateDecision]]:
    decisions = [evaluate_gate(summary) for summary in summaries.values()]
    by_alias = {decision.candidate_alias: decision for decision in decisions}
    for eligible_alias in ("primary", "challenger"):
        decision = by_alias.get(eligible_alias)
        if decision is not None and decision.passed:
            return eligible_alias, decisions
    return None, decisions
