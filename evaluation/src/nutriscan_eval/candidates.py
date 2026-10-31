from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Candidate:
    alias: str
    routed_model: str
    provider: str
    input_usd_per_million: Decimal
    output_usd_per_million: Decimal
    production_eligible: bool

    @property
    def model(self) -> str:
        return self.routed_model.removesuffix(f":{self.provider}")


CANDIDATES = {
    candidate.alias: candidate
    for candidate in (
        Candidate(
            alias="primary",
            routed_model="Qwen/Qwen3.5-9B:deepinfra",
            provider="deepinfra",
            input_usd_per_million=Decimal("0.10"),
            output_usd_per_million=Decimal("0.15"),
            production_eligible=True,
        ),
        Candidate(
            alias="challenger",
            routed_model="Qwen/Qwen3-VL-30B-A3B-Instruct:deepinfra",
            provider="deepinfra",
            input_usd_per_million=Decimal("0.15"),
            output_usd_per_million=Decimal("0.60"),
            production_eligible=True,
        ),
        Candidate(
            alias="baseline",
            routed_model="google/gemma-3-4b-it:deepinfra",
            provider="deepinfra",
            input_usd_per_million=Decimal("0.05"),
            output_usd_per_million=Decimal("0.10"),
            production_eligible=False,
        ),
    )
}

PRICE_SNAPSHOT_DATE = "2026-10-26"
DEFAULT_CANDIDATE_ORDER = ("primary", "challenger", "baseline")


def get_candidates(aliases: list[str] | tuple[str, ...]) -> list[Candidate]:
    unknown = sorted(set(aliases) - CANDIDATES.keys())
    if unknown:
        raise ValueError(f"Unknown candidate aliases: {', '.join(unknown)}")
    return [CANDIDATES[alias] for alias in aliases]
