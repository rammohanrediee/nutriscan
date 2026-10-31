# Vision model selection for NutriScan

**Status:** Pre-benchmark. No production model has been selected.

**Evidence checked:** 26 October 2026. Provider availability, pricing, licenses, and privacy terms
must be checked again immediately before a paid run.

## Product requirement

NutriScan needs a hosted vision-language model that can examine one food photograph, suggest zero
or more visible Indian dishes, offer rough household portions, and return strict structured JSON.
The output is a **Recognition Suggestion**, never nutrition and never a confirmed fact.

The model must work for single dishes and mixed home, restaurant, and thali meals. A fixed-class,
single-label image classifier is therefore insufficient even if its accuracy is high on its own
training distribution.

## Shortlist

| Role | Routed model | License | DeepInfra price snapshot (input/output per 1M tokens) | Reason |
| --- | --- | --- | --- | --- |
| Primary | `Qwen/Qwen3.5-9B:deepinfra` | Apache-2.0 | $0.10 / $0.15 | Native multimodal model, structured output, low cost |
| Challenger | `Qwen/Qwen3-VL-30B-A3B-Instruct:deepinfra` | Apache-2.0 | $0.15 / $0.60 | Larger vision-language challenger |
| Baseline only | `google/gemma-3-4b-it:deepinfra` | Gemma terms | $0.05 / $0.10 | Cheap calibration point; gated license |

Primary sources:

- [Qwen3.5-9B model card](https://huggingface.co/Qwen/Qwen3.5-9B)
- [Qwen3-VL-30B-A3B-Instruct model card](https://huggingface.co/Qwen/Qwen3-VL-30B-A3B-Instruct)
- [Gemma 3 4B model card](https://huggingface.co/google/gemma-3-4b-it)
- [Hugging Face routed model capabilities and prices](https://huggingface.co/inference/models)
- [Hugging Face structured-output API](https://huggingface.co/docs/inference-providers/en/guides/structured-output)

The benchmark pins `deepinfra` so all candidates use the same routing surface. Hugging Face says it
does not store routed request bodies or responses, while external provider policies still apply.
DeepInfra's current terms state that inference customer data is deleted after processing and is not
used for training, with listed operational and legal exceptions.

- [Hugging Face Inference Providers security](https://huggingface.co/docs/inference-providers/security)
- [DeepInfra terms](https://deepinfra.com/terms)

## Why specialized classifiers are not the main candidates

[`prithivMLmods/Indian-Western-Food-34`](https://huggingface.co/prithivMLmods/Indian-Western-Food-34)
is a single-label classifier with a fixed 34-class vocabulary and is not deployed by a Hugging Face
Inference Provider. It cannot enumerate a mixed plate or express structured alternatives and
portions.

The [SmartPlate model card](https://huggingface.co/spaces/Aishrica/SmartPlate/blob/main/MODEL_CARD.md)
reports roughly 75% test accuracy from only 50 images per class and explicitly says the model
assumes one dominant dish and does not estimate portions or detect multiple foods. These models can
be useful research references but do not meet NutriScan's interface.

## Evaluation data

The selection authority is one private, held-out set of exactly 30 product-owner photographs. Each
manifest row has one primary `benchmark_category`; scenario tags may overlap. The required primary
distribution is:

- 12 everyday Indian tiffin or home-meal images;
- 8 protein-focused meal images;
- 5 fruit, vegetable, or salad images;
- 2 indulgent or street-food images; and
- 3 unclear or non-food controls.

The set must contain at least ten mixed meals and collectively cover home, restaurant, thali,
takeaway, low-light, occluded, and visually confusing-pair scenarios. Every food image needs
human-reviewed expected foods and rough visible-portion notes. Controls have no expected foods.
Private files, labels, and predictions remain gitignored and must not be used for training, prompt
tuning, or iterative candidate-specific correction.

The older 75-image public set is retained only as a reproducible diagnostic. It uses five
deterministic examples for each of the 15 classes in
[`bharat-raghunathan/indian-foods-dataset`](https://huggingface.co/datasets/bharat-raghunathan/indian-foods-dataset),
whose Hub card declares CC0, pinned at revision
`ef509a8b4bfd46b76530ad329f81586faf904aad`. Its single-dish top-1 accuracy appears in reports but
cannot pass or fail a candidate because the set is narrow, snack-heavy, and not representative of
NutriScan's mixed-meal product distribution.

## Pass gate

A candidate passes only when it has:

- exactly the required 30-image private category distribution;
- 100% schema-valid responses on the private benchmark;
- at least 0.75 item-level F1 across all 27 private food images;
- at least ten mixed meals and at least 0.75 item-level F1 on those mixed meals;
- usable structured portions on at least 80% of correctly matched foods, meaning a positive
  quantity and a non-`unknown` allowed unit;
- private-benchmark p95 latency no greater than 10 seconds;
- private-benchmark mean estimated cost no greater than US$0.01 per scan;
- no nutrition leakage on the private benchmark; and
- correct abstention on all three unclear/non-food controls.

The portion gate measures whether the model returns a usable rough household portion, not whether
it knows exact grams from a single photograph. Numeric portion accuracy requires measured ground
truth and remains a later research question; human notes are retained for review and future
agreement studies. Public diagnostic accuracy is reported separately and is not a pass criterion.

Selection order is deterministic: choose Qwen3.5-9B if it passes; otherwise choose the 30B Qwen
challenger if it passes. Gemma is never selected without a separate license review. If neither Qwen
passes, preserve the evidence and stop product implementation.

## Pending evidence

1. A scoped `HF_TOKEN` with Inference Providers permission.
2. Successful in-memory data-URL transport spike for each candidate.
3. Prepared 75-image public diagnostic manifest.
4. Valid product-weighted private manifest and exactly 30 photographs.
5. Completed result summary within the US$5 total budget.
6. An accepted ADR recording the winning model and replacement criteria.

