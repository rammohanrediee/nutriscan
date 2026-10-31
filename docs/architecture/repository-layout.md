# Repository layout and product surfaces

NutriScan has three intentionally separate product areas plus the model evaluation workspace.

```text
NutriScan/
├── backend/                        # FastAPI modular monolith
│   ├── migrations/
│   ├── src/nutriscan/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   └── features/
│   └── tests/
├── frontend/                       # desktop web landing page only
│   ├── public/
│   └── src/
│       ├── app/
│       ├── components/
│       ├── sections/
│       └── styles/
├── mobile/                         # complete Android and iOS product
│   ├── app/                        # Expo Router routes
│   ├── assets/
│   └── src/
│       ├── components/
│       ├── core/
│       ├── features/
│       ├── services/
│       ├── storage/
│       └── theme/
├── evaluation/                     # model-selection harness
└── docs/
```

## Backend

The backend uses Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy 2 async, Alembic, Pydantic v2,
pytest, Ruff, and uv after the gate passes. `backend/src/nutriscan/features/` is the modular-monolith
center; see `modular-monolith.md`.

## Frontend

`frontend/` serves only a desktop-friendly public landing page: product explanation, supported
platforms, privacy summary, and links to obtain the mobile app. It must not contain scanning,
nutrition review, meal history, authentication, or a desktop dashboard.

No web framework has been selected in the approved technical stack. Do not add one implicitly; make
that decision when landing-page implementation is authorized.

## Mobile

`mobile/` is the actual product. It will use React Native, Expo, TypeScript, Expo Router, Expo Camera
and Image Picker, Expo SQLite, and secure storage where necessary. Camera capture, analysis state,
food review, nutrition results, and local meal history all belong here.

Expo Router files in `mobile/app/` stay thin. Product behavior and reusable UI live under
`mobile/src/features/` and `mobile/src/components/`.

## Current gate

The directories exist now to make ownership visible in the repository. Their README files are not
runtime scaffolding. Do not add dependencies or implementation until the model-selection gate
records a winner.
