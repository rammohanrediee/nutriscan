from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ImageStatus(StrEnum):
    FOOD = "food"
    NOT_FOOD = "not_food"
    UNCLEAR = "unclear"


class PortionUnit(StrEnum):
    PIECE = "piece"
    KATORI = "katori"
    CUP = "cup"
    TABLESPOON = "tablespoon"
    GRAM = "gram"
    SERVING = "serving"
    UNKNOWN = "unknown"


class DetectedFood(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    quantity: float | None = Field(default=None, gt=0)
    unit: PortionUnit
    alternatives: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("food name cannot be blank")
        return value

    @field_validator("alternatives")
    @classmethod
    def clean_alternatives(cls, values: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for raw_value in values:
            value = " ".join(raw_value.split())
            key = value.casefold()
            if value and key not in seen:
                seen.add(key)
                result.append(value)
        return result

    @model_validator(mode="after")
    def remove_name_from_alternatives(self) -> "DetectedFood":
        own_name = self.name.casefold()
        self.alternatives = [item for item in self.alternatives if item.casefold() != own_name]
        return self


class RecognitionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_status: ImageStatus
    detected_foods: list[DetectedFood] = Field(default_factory=list, max_length=20)
    needs_user_review: Literal[True]

    @model_validator(mode="after")
    def validate_status_and_foods(self) -> "RecognitionResult":
        if self.image_status is ImageStatus.FOOD and not self.detected_foods:
            raise ValueError("food status requires at least one detected food")
        if self.image_status is not ImageStatus.FOOD and self.detected_foods:
            raise ValueError("not_food and unclear responses must have an empty food list")
        return self


class ProviderUsage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class BenchmarkRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: Literal["public", "private", "smoke"]
    image_id: str
    benchmark_category: str
    scenario: str
    candidate_alias: str
    model: str
    provider: str
    expected_foods: list[str]
    prediction: RecognitionResult | None
    normalized_foods: list[str] = Field(default_factory=list)
    schema_valid: bool
    latency_seconds: float = Field(ge=0)
    usage: ProviderUsage
    estimated_cost_usd: str
    error_code: str | None = None
    nutrition_leak: bool = False
    run_timestamp: str
