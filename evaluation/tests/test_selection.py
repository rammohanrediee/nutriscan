from dataclasses import replace

from nutriscan_eval.metrics import CandidateSummary
from nutriscan_eval.selection import evaluate_gate, select_winner


def _passing(alias: str) -> CandidateSummary:
    return CandidateSummary(
        candidate_alias=alias,
        total_examples=105,
        public_examples=75,
        public_top1_accuracy=0.8,
        private_examples=30,
        private_category_counts={
            "everyday": 12,
            "protein": 8,
            "produce": 5,
            "indulgent": 2,
            "control": 3,
        },
        private_schema_valid_rate=1.0,
        private_item_precision=0.75,
        private_item_recall=0.75,
        private_item_f1=0.75,
        private_mixed_examples=10,
        private_mixed_precision=0.75,
        private_mixed_recall=0.75,
        private_mixed_f1=0.75,
        private_portion_matches=20,
        private_portion_complete_rate=0.8,
        private_p95_latency_seconds=10,
        private_mean_cost_usd=0.01,
        private_nutrition_leaks=0,
        unclear_controls=3,
        unclear_control_pass_rate=1.0,
    )


def test_primary_wins_when_both_qwen_candidates_pass() -> None:
    winner, _ = select_winner(
        {"challenger": _passing("challenger"), "primary": _passing("primary")}
    )
    assert winner == "primary"


def test_challenger_wins_only_after_primary_fails() -> None:
    primary = replace(_passing("primary"), private_item_f1=0.74)
    winner, decisions = select_winner({"primary": primary, "challenger": _passing("challenger")})
    assert winner == "challenger"
    assert not next(item for item in decisions if item.candidate_alias == "primary").passed


def test_baseline_cannot_be_selected() -> None:
    winner, _ = select_winner({"baseline": _passing("baseline")})
    assert winner is None


def test_each_gate_has_an_explicit_failure() -> None:
    decision = evaluate_gate(replace(_passing("primary"), private_nutrition_leaks=1))
    assert not decision.passed
    assert "model generated nutrition language" in decision.failures


def test_public_diagnostic_accuracy_does_not_affect_gate() -> None:
    decision = evaluate_gate(
        replace(_passing("primary"), public_examples=0, public_top1_accuracy=0.0)
    )
    assert decision.passed
