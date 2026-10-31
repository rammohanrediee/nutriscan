# Backend placeholder

This directory reserves the approved FastAPI modular-monolith shape. Runtime setup remains blocked
until model selection succeeds.

The Python package will live under `src/nutriscan/` with `api`, `core`, `db`, and `features` as its
top-level areas. The first reserved feature modules are `recognition`, `catalog`, and `nutrition`.
`meals` and `identity` are added when their behavior is authorized and required.

The proposed runtime files remain deferred, including `pyproject.toml`, `main.py`, API routers,
configuration, database setup, schemas, models, repositories, services, calculators, and provider
adapters. The vision adapter will be owned by the `recognition` feature rather than a global
`integrations` package. This keeps provider details behind the feature boundary and prevents other
features from depending on them directly.

See `../docs/architecture/modular-monolith.md` before adding backend code.

