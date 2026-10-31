from dataclasses import dataclass
from decimal import Decimal

from .candidates import Candidate
from .schemas import ProviderUsage

ONE_MILLION = Decimal(1_000_000)
HARD_BENCHMARK_CAP_USD = Decimal("5.00")


def estimate_cost(usage: ProviderUsage, candidate: Candidate) -> Decimal:
    input_cost = Decimal(usage.prompt_tokens) * candidate.input_usd_per_million / ONE_MILLION
    output_cost = Decimal(usage.completion_tokens) * candidate.output_usd_per_million / ONE_MILLION
    return (input_cost + output_cost).quantize(Decimal("0.00000001"))


class BudgetExceeded(RuntimeError):
    pass


@dataclass(slots=True)
class BudgetLedger:
    cap_usd: Decimal = Decimal("5.00")
    reserve_per_request_usd: Decimal = Decimal("0.02")
    spent_usd: Decimal = Decimal("0")
    _reserved_usd: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.cap_usd <= 0:
            raise ValueError("Budget cap must be greater than zero")
        if self.cap_usd > HARD_BENCHMARK_CAP_USD:
            raise ValueError("Budget cap cannot exceed the hard US$5 limit")
        if self.reserve_per_request_usd <= 0:
            raise ValueError("Request reserve must be greater than zero")

    def reserve_request(self) -> None:
        projected = self.spent_usd + self._reserved_usd + self.reserve_per_request_usd
        if projected > self.cap_usd:
            raise BudgetExceeded(
                f"Budget circuit breaker: projected ${projected} exceeds ${self.cap_usd} cap"
            )
        self._reserved_usd += self.reserve_per_request_usd

    def commit_request(self, actual_cost_usd: Decimal) -> None:
        if self._reserved_usd < self.reserve_per_request_usd:
            raise RuntimeError("No request reservation to commit")
        projected = self.spent_usd + actual_cost_usd
        if projected > self.cap_usd:
            raise BudgetExceeded(f"Provider-reported cost ${projected} exceeds ${self.cap_usd} cap")
        self._reserved_usd -= self.reserve_per_request_usd
        self.spent_usd = projected

    def release_request(self) -> None:
        if self._reserved_usd >= self.reserve_per_request_usd:
            self._reserved_usd -= self.reserve_per_request_usd
