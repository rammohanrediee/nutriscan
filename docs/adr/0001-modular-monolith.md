# ADR 0001: Use a modular monolith for the backend

- **Status:** Accepted
- **Date:** 2026-10-26
- **Decision owner:** Product owner

## Context

NutriScan needs recognition, user review, food catalog matching, nutrition calculation, meal
history, and eventually identity. These capabilities need clear ownership, but an MVP does not need
the operational cost or distributed failure modes of microservices.

A conventional horizontal layout with global `routes`, `services`, `models`, and `repositories`
would scatter each feature across the codebase and make cross-feature coupling easy. NutriScan also
has a safety-critical seam: untrusted vision output must not become trusted nutrition without review
and catalog matching.

## Decision

Build the backend as one deployable Python application and one database. The Python package lives
at `backend/src/nutriscan/` with `api`, `core`, `db`, and `features` at its top level, matching the
approved repository format. Each directory under `features` is a module that owns its domain
behavior, application workflows, persistence implementation, and adapters. It exposes one
deliberately small public interface to the rest of the monolith.

Initial modules are:

- `recognition`: image preprocessing, selected vision adapter, schema validation, and Recognition
  Suggestions
- `catalog`: canonical foods, aliases, and reviewed matching
- `nutrition`: deterministic nutrition calculation from canonical foods and confirmed portions
- `meals`: scan lifecycle, user review, confirmed meal items, and history
- `identity`: accounts and preferences, introduced only when authentication is required

The application entry point is the composition root. It creates adapters and injects them into
modules. HTTP routes translate transport input and output; they contain no business rules.

## Module rules

1. A module's public `interface.py` is the only supported cross-module import.
2. Domain code does not import HTTP, database, provider SDK, or another module's implementation.
3. A module owns its tables and persistence queries. Another module cannot read those tables
   directly.
4. Cross-module work is coordinated through public commands and returned results in the same
   process, not internal HTTP calls.
5. `core` contains only application-wide platform concerns such as configuration, observability,
   time, identifiers, and transaction primitives. It is not a miscellaneous business-logic folder.
6. New interfaces are introduced only when behavior actually varies or a second adapter exists.
7. Recognition output remains an untrusted Recognition Suggestion. Nutrition accepts only reviewed,
   catalog-resolved food and portion input.

## Consequences

- One process and database keep deployment, transactions, debugging, and local development simple.
- Feature behavior stays local and can be tested through the same interface used by callers.
- Module ownership makes a later extraction possible if measured scaling or team constraints demand
  it; extraction is not a present goal.
- Engineers must actively enforce import and table-ownership rules because process isolation will
  not enforce them.

## Deferred work

This ADR chooses the structure only. Placeholder directories and ownership notes may exist, but
runtime setup, database migrations, HTTP routes, landing-page code, mobile code, and production
adapters remain blocked until the vision-model selection gate passes.

