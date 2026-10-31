# Production and release authority

NutriScan is not deployable yet. This document owns deployment, operations, and release gates. It
links to technical authorities instead of repeating their detailed decisions.

## Current state

- The vision-model gate has not selected a production model.
- Backend and mobile directories contain ownership placeholders, not runtime applications.
- No production environment, deployment provider, account system, or public API is approved.
- Nutrition data cannot ship until its product-use rights and attribution requirements are clear.

## Environments and configuration

Introduce local, test, staging, and production configuration only when an active tracker episode
needs them. Secrets stay outside source control and logs. Provider tokens must be scoped, rotated,
and held by the backend; they must never be embedded in the React Native bundle.

## Data and privacy

- Meal photographs and private benchmark labels are private data.
- Do not commit photographs, private predictions, tokens, or benchmark artifacts.
- Define retention and deletion behavior before a deployed service accepts user photographs.
- Logs may contain identifiers and timing, but not image bytes, tokens, raw private predictions, or
  full user-entered meal details.
- A model response is untrusted input. Only user-reviewed, catalog-resolved foods may reach
  nutrition calculation.

## External model behavior

Every production provider integration requires bounded timeouts, validated structured output,
cost limits, safe errors, and an explicit unavailable-model experience. Provider output never
grants identity, authorization, data ownership, or nutrition authority.

## Operational decisions still deferred

Deployment hosting, database operations, migrations, backups, restore drills, monitoring, rate
limits, account recovery, and incident response are chosen only when their tracker season becomes
active. Their absence is deliberate and must not be described as implemented.

## Ordered release gates

1. The model-selection benchmark passes and an accepted ADR records the winning model and provider.
2. The React Native/Expo and backend vertical slice passes its legitimate and failure-path tests.
3. Nutrition sources have documented product-use rights, provenance, units, and validation.
4. Image upload, provider output, local storage, and deletion boundaries have security regression
   evidence and equivalent legitimate-use controls.
5. Deployment configuration, secret handling, observability, rollback, and backup/restore behavior
   are documented and exercised for the chosen environment.
6. Mobile permission, accessibility, privacy disclosure, and release-build checks pass on supported
   Android and iOS targets.

The detailed first gate remains authoritative in
[`docs/research/vision-model-selection.md`](docs/research/vision-model-selection.md).
