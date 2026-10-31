# NutriScan model evaluation

This Python 3.12 workspace prepares and scores the model-selection benchmark. It does not contain
the mobile app, a production API, nutrition calculation, training, or fine-tuning.

## Setup

Run setup from the evaluation workspace. Its `.python-version` pins Python 3.12; do not install
this package into a repository-root environment that uses another Python version.

```bash
cd evaluation
uv python install 3.12
uv sync
uv run python --version
cp .env.example .env
```

The version check must report Python 3.12.x. Use `uv run ...` for the commands below so uv selects
the pinned environment even when another virtual environment is active in the parent directory.

Create a narrowly scoped Hugging Face token with Inference Providers permission and put it in the
ignored `.env` file. Do not paste the token into chat, source code, command history, or commits.

## Private evaluation set

Put exactly 30 representative files in `private/images/` and use
`private-labels.example.csv` as the schema for `private/labels.csv`. Separate expected foods and
overlapping scenario tags with `|`. Assign one primary `benchmark_category` to every image using
the required distribution: 12 `everyday`, 8 `protein`, 5 `produce`, 2 `indulgent`, and 3
`control`. Include at least ten mixed meals and cover home, restaurant, thali, takeaway,
low-light, occlusion, and confusing-pair scenarios. Controls have an empty `expected_foods` cell;
every food image needs human-reviewed `portion_notes`. Everything under `private/` is ignored by
Git.

Validate before spending credit:

```bash
uv run nutriscan-eval validate-private \
  --images private/images \
  --manifest private/labels.csv
```

## Public diagnostic set

The command below streams the dataset test split and saves exactly five deterministic examples
from each of its 15 classes. Its top-1 accuracy is reported for comparison but does not participate
in the model-selection pass gate:

```bash
uv run nutriscan-eval prepare-public --output artifacts/public
```

`artifacts/` is intentionally ignored because generated images and predictions should not enter
the repository.

## Live transport smoke test

Source `.env`, then run one request per candidate. The request embeds the image as an in-memory
data URL; it never uploads the file to a public URL.

```bash
set -a
source .env
set +a
uv run nutriscan-eval smoke \
  --image private/images/example.jpg \
  --confirm-current-terms
```

If data-URL image input or strict JSON output fails for a candidate, stop. Do not work around it
with a public image URL.

## Full benchmark

```bash
uv run nutriscan-eval run \
  --public-images artifacts/public/images \
  --public-manifest manifests/public.csv \
  --private-images private/images \
  --private-manifest private/labels.csv \
  --output artifacts/results \
  --confirm-current-terms
```

Immediately before either live command, recheck the provider table, model licenses, Hugging Face
security guidance, and DeepInfra terms linked in `docs/research/vision-model-selection.md`. Live
commands also refuse to run after the dated price snapshot becomes stale.

The default and maximum hard budget cap is US$5. Results store normalized, redacted records and
aggregate scores, never raw provider responses or private image paths. Selection uses private
item-level and mixed-meal F1, private schema/latency/cost/leakage results, control abstention, and
usable portion coverage. A portion is usable when a correctly matched food has a positive quantity
and a non-`unknown` allowed unit; this is not a claim of exact gram accuracy.

## Offline verification

```bash
uv run ruff check .
uv run pytest
```

