# NutriScan model evaluation

NutriScan is evaluating vision models for recognizing Indian meals. This repository contains the
evaluation harness and product plans. The Expo app and production FastAPI backend will be built
after a model passes the selection criteria.

## Product direction

NutriScan is a mobile-first food-recognition and nutrition-tracking product for people recording
everyday Indian meals, including diet-conscious and fitness-focused users. Its recognition
benchmark prioritizes routine tiffins and home meals, protein-focused foods, fruit, vegetables,
salads, and realistic mixed plates. Indulgent and street foods remain supported but are not the
primary evaluation distribution.

The planned meal-recording flow is:

1. The user takes or selects a meal photograph in the mobile app.
2. A vision model returns an untrusted Recognition Suggestion.
3. The user reviews and corrects foods and visible portions.
4. Catalog resolves the confirmed names to canonical foods.
5. Nutrition calculates estimates from confirmed quantities and a licensed composition source.
6. The mobile app stores the confirmed meal in local history.

The React Native and Expo app will live under `mobile/`, with a desktop landing page under
`frontend/`. The backend will be a modular monolith under `backend/`; its module boundaries are
defined in `docs/architecture/modular-monolith.md`. These directories currently contain
placeholders.

The evaluation harness compares three Hugging Face vision-language candidates. Selection depends
on a private set of exactly 30 meal and control photographs. The older 75-image public Indian-food
set provides diagnostic results only. See
[`evaluation/README.md`](evaluation/README.md) for the commands and
[`docs/research/vision-model-selection.md`](docs/research/vision-model-selection.md) for the
evidence and decision gate.

## Current status

- Candidate research: complete for the initial shortlist.
- Reproducible benchmark harness: included.
- Backend, landing-page, and mobile directory ownership: documented with placeholders only.
- Public benchmark images: prepared on demand and never committed.
- Private benchmark images: waiting for the product-weighted set of exactly 30 user-supplied
  examples.
- External dataset supplements: source rights and provenance remain unapproved.
- Production model: not selected.
- Application implementation: blocked until an Apache-2.0 Qwen candidate passes every gate.

## Documentation

- Product behavior, users, journey, and current status: this README
- Domain language: [`CONTEXT.md`](CONTEXT.md)
- Backend boundaries: [`docs/architecture/modular-monolith.md`](docs/architecture/modular-monolith.md)
- Repository ownership and product surfaces:
  [`docs/architecture/repository-layout.md`](docs/architecture/repository-layout.md)
- Durable architectural decisions: [`docs/adr/`](docs/adr/)
- Model-selection evidence and gate:
  [`docs/research/vision-model-selection.md`](docs/research/vision-model-selection.md)
- Deployment, operations, and release gates: [`PRODUCTION.md`](PRODUCTION.md)

