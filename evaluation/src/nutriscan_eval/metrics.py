import math
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from .normalization import normalized_food_set
from .schemas import BenchmarkRecord, DetectedFood, ImageStatus, PortionUnit


@dataclass(frozen=True, slots=True)
class CandidateSummary:
    candidate_alias: str
    total_examples: int
    public_examples: int
    public_top1_accuracy: float
    private_examples: int
    private_category_counts: dict[str, int]
    private_schema_valid_rate: float
    private_item_precision: float
    private_item_recall: float
    private_item_f1: float
    private_mixed_examples: int
    private_mixed_precision: float
    private_mixed_recall: float
    private_mixed_f1: float
    private_portion_matches: int
    private_portion_complete_rate: float
    private_p95_latency_seconds: float
    private_mean_cost_usd: float
    private_nutrition_leaks: int
    unclear_controls: int
    unclear_control_pass_rate: float

    def as_dict(self) -> dict[str, str | int | float | dict[str, int]]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


def percentile(values: Iterable[float], percentile_value: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, math.ceil(percentile_value * len(ordered)) - 1)
    return ordered[index]


def _food_names(food: DetectedFood) -> set[str]:
    return normalized_food_set([food.name, *food.alternatives])


def top1_is_correct(record: BenchmarkRecord) -> bool:
    if not record.schema_valid or record.prediction is None or not record.expected_foods:
        return False
    if not record.prediction.detected_foods:
        return False
    expected = normalized_food_set(record.expected_foods)
    return bool(_food_names(record.prediction.detected_foods[0]) & expected)


def item_match_counts(record: BenchmarkRecord) -> tuple[int, int, int]:
    matched_prediction_indexes = _matched_prediction_indexes(record)
    expected = normalized_food_set(record.expected_foods)
    predicted = record.prediction.detected_foods if record.prediction is not None else []
    matched = len(matched_prediction_indexes)
    false_positive = max(0, len(predicted) - matched)
    false_negative = len(expected) - matched
    return matched, false_positive, false_negative


def _matched_prediction_indexes(record: BenchmarkRecord) -> set[int]:
    expected = normalized_food_set(record.expected_foods)
    predicted = record.prediction.detected_foods if record.prediction is not None else []
    options = [_food_names(food) & expected for food in predicted]
    matched_expected: dict[str, int] = {}

    def assign(prediction_index: int, seen: set[str]) -> bool:
        for expected_name in sorted(options[prediction_index]):
            if expected_name in seen:
                continue
            seen.add(expected_name)
            previous = matched_expected.get(expected_name)
            if previous is None or assign(previous, seen):
                matched_expected[expected_name] = prediction_index
                return True
        return False

    for index in range(len(predicted)):
        assign(index, set())
    return set(matched_expected.values())


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def aggregate_candidate(records: list[BenchmarkRecord]) -> CandidateSummary:
    if not records:
        raise ValueError("At least one benchmark record is required")
    aliases = {record.candidate_alias for record in records}
    if len(aliases) != 1:
        raise ValueError("Records must belong to exactly one candidate")

    public = [record for record in records if record.scope == "public"]
    private = [record for record in records if record.scope == "private"]
    private_food = [record for record in private if normalized_food_set(record.expected_foods)]
    mixed = [
        record
        for record in records
        if record.scope == "private" and len(normalized_food_set(record.expected_foods)) >= 2
    ]
    controls = [
        record
        for record in records
        if record.scope == "private" and not normalized_food_set(record.expected_foods)
    ]

    def recognition_counts(
        selected_records: list[BenchmarkRecord],
    ) -> tuple[int, int, int, float, float, float]:
        true_positive = false_positive = false_negative = 0
        for record in selected_records:
            matched, extra, missed = item_match_counts(record)
            true_positive += matched
            false_positive += extra
            false_negative += missed
        precision = _ratio(true_positive, true_positive + false_positive)
        recall = _ratio(true_positive, true_positive + false_negative)
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return true_positive, false_positive, false_negative, precision, recall, f1

    _, _, _, item_precision, item_recall, item_f1 = recognition_counts(private_food)
    _, _, _, mixed_precision, mixed_recall, mixed_f1 = recognition_counts(mixed)

    portion_matches = portion_complete = 0
    for record in private_food:
        predicted = record.prediction.detected_foods if record.prediction is not None else []
        matched_indexes = _matched_prediction_indexes(record)
        portion_matches += len(matched_indexes)
        portion_complete += sum(
            predicted[index].quantity is not None
            and predicted[index].unit is not PortionUnit.UNKNOWN
            for index in matched_indexes
        )

    category_counts: dict[str, int] = {}
    for record in private:
        category_counts[record.benchmark_category] = (
            category_counts.get(record.benchmark_category, 0) + 1
        )

    private_costs = [Decimal(record.estimated_cost_usd) for record in private]
    private_mean_cost = (
        float(sum(private_costs, Decimal("0")) / len(private_costs)) if private_costs else 0.0
    )

    control_passes = sum(
        record.schema_valid
        and record.prediction is not None
        and record.prediction.image_status in {ImageStatus.NOT_FOOD, ImageStatus.UNCLEAR}
        and not record.prediction.detected_foods
        for record in controls
    )
    return CandidateSummary(
        candidate_alias=aliases.pop(),
        total_examples=len(records),
        public_examples=len(public),
        public_top1_accuracy=_ratio(sum(top1_is_correct(record) for record in public), len(public)),
        private_examples=len(private),
        private_category_counts=category_counts,
        private_schema_valid_rate=_ratio(
            sum(record.schema_valid for record in private), len(private)
        ),
        private_item_precision=item_precision,
        private_item_recall=item_recall,
        private_item_f1=item_f1,
        private_mixed_examples=len(mixed),
        private_mixed_precision=mixed_precision,
        private_mixed_recall=mixed_recall,
        private_mixed_f1=mixed_f1,
        private_portion_matches=portion_matches,
        private_portion_complete_rate=_ratio(portion_complete, portion_matches),
        private_p95_latency_seconds=percentile(
            (record.latency_seconds for record in private), 0.95
        ),
        private_mean_cost_usd=private_mean_cost,
        private_nutrition_leaks=sum(record.nutrition_leak for record in private),
        unclear_controls=len(controls),
        unclear_control_pass_rate=_ratio(control_passes, len(controls)),
    )
