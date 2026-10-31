# NutriScan modular monolith

The production backend will use the approved Python package shape:

```text
backend/
├── migrations/
├── src/
│   └── nutriscan/
│       ├── main.py                 # future composition root
│       ├── api/                    # FastAPI transport only
│       ├── core/                   # configuration and platform primitives
│       ├── db/                     # session, transaction, and migration infrastructure
│       └── features/               # business modules
│           ├── recognition/
│           ├── catalog/
│           ├── nutrition/
│           ├── meals/
│           └── identity/
└── tests/
```

The current repository contains ownership notes only. `main.py`, runtime configuration, database
models, routes, and feature implementations are created only after the model-selection gate passes.

## Folder responsibilities

- `api` translates HTTP requests, responses, authentication context, and errors. It contains no
  business rules.
- `core` contains application-wide platform concerns such as configuration, observability, time,
  identifiers, and transaction primitives. It is not a miscellaneous folder.
- `db` owns SQLAlchemy engine/session setup, the declarative base, and migration integration. It
  does not own feature-specific queries.
- `features` contains the modular monolith. Every child directory is a feature module with its own
  domain rules, workflows, persistence implementation, and adapters.

## Feature-module shape

Create files only when real behavior requires them. A mature feature may look like this:

```text
features/recognition/
├── interface.py                    # only supported cross-feature import
├── domain.py
├── application.py
├── persistence.py
└── adapters/
    └── vision_provider.py
```

Avoid global `models`, `schemas`, `repositories`, and `services` directories. Those layouts scatter
one feature across the entire backend. Package-marker files are omitted from these diagrams.

## Dependency direction

```text
HTTP transport → feature interface → feature implementation → owned adapters
                            ↓
                    domain values and rules
```

The composition root can see every feature so it can wire the process. A feature cannot import
another feature's `domain.py`, `application.py`, `persistence.py`, database tables, or adapters. It
may import only that feature's `interface.py`.

The initial dependency graph is acyclic:

- `recognition`, `catalog`, and `nutrition` do not depend on other business features.
- `meals` coordinates the scan workflow through the public interfaces of those three features.
- `identity` supplies an authenticated actor without owning meal behavior.
- `api` calls feature interfaces; features never import `api`.

## Recognition workflow

1. `meals` starts a scan and supplies an image reference to `recognition`.
2. `recognition` preprocesses the image and calls the selected `VisionProvider`.
3. `recognition` validates and returns a Recognition Suggestion.
4. The mobile user reviews names and portions.
5. `catalog` resolves reviewed names to canonical food identifiers.
6. `nutrition` calculates values from catalog data and confirmed portions.
7. `meals` records the confirmed items and calculated nutrition.

Steps 4–6 cannot be skipped. `recognition` has no interface for producing calories or nutrients.

## Module interfaces

Keep interfaces small and workflow-oriented. Prefer operations such as `suggest_foods`,
`resolve_foods`, `calculate_nutrition`, and `confirm_meal` over generic CRUD interfaces. Accept
dependencies at construction, return results rather than mutating caller state, and keep provider
and database types behind adapters.

The evaluation `VisionProvider` is evidence for a future seam, not production backend code. After a
model wins, promote its contract deliberately instead of importing the evaluation package.

## Enforcement when implementation begins

- Add import tests that reject cross-feature implementation imports.
- Give each feature explicit ownership of its tables and queries.
- Test behavior through feature interfaces and adapters through integration tests.
- Keep HTTP tests focused on transport translation and error mapping.
- Record exceptions to these rules in an ADR before merging them.

