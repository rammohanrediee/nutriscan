# NutriScan Domain

Shared product language for recognizing Indian meals without treating model output as verified
nutrition or fact.

## Language

**Recognition Suggestion**:
An untrusted proposal from a vision model about food that may be visible in one image, including
possible names and a rough portion. A person must review it before nutrition is calculated.
_Avoid_: Detection result, identified food, confirmed food

**Modular Monolith**:
One deployable backend whose business capabilities are implemented as isolated feature modules.
Modules run in the same process and database, but callers cross only explicit public interfaces.
_Avoid_: Microservices, globally layered service/repository folders, direct cross-module table use

## Backend modules

- **Recognition** creates a Recognition Suggestion from an image through a `VisionProvider`.
- **Catalog** resolves reviewed food names to canonical food records.
- **Nutrition** calculates nutrition from confirmed catalog foods and portions; vision output is
  never accepted as nutrition.
- **Meals** owns scans, review state, confirmed meal items, and meal history.
- **Identity** owns accounts, sessions, and user preferences when authentication is introduced.

See `docs/architecture/modular-monolith.md` for dependency rules and the deferred directory shape.

## Product surfaces

- **Backend** is the FastAPI modular monolith under `backend/src/nutriscan/`.
- **Frontend** is a desktop web landing page only. It must not grow authenticated product features.
- **Mobile** is the Android and iOS product built with React Native and Expo after model selection.

See `docs/architecture/repository-layout.md` for ownership and the complete repository shape.

