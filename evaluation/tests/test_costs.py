from decimal import Decimal

import pytest

from nutriscan_eval.candidates import CANDIDATES
from nutriscan_eval.costs import BudgetExceeded, BudgetLedger, estimate_cost
from nutriscan_eval.schemas import ProviderUsage


def test_cost_estimate_uses_candidate_rates() -> None:
    cost = estimate_cost(
        ProviderUsage(prompt_tokens=1_000_000, completion_tokens=100_000, total_tokens=1_100_000),
        CANDIDATES["primary"],
    )
    assert cost == Decimal("0.11500000")


def test_budget_circuit_breaker_stops_before_reservation_exceeds_cap() -> None:
    ledger = BudgetLedger(cap_usd=Decimal("0.03"), reserve_per_request_usd=Decimal("0.02"))
    ledger.reserve_request()
    ledger.commit_request(Decimal("0.015"))
    with pytest.raises(BudgetExceeded):
        ledger.reserve_request()


def test_budget_cannot_be_configured_above_hard_limit() -> None:
    with pytest.raises(ValueError, match=r"hard US\$5 limit"):
        BudgetLedger(cap_usd=Decimal("5.01"))
