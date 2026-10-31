# ADR 0002: Keep the product mobile-first and the desktop web surface informational

- **Status:** Accepted
- **Date:** 2026-10-26
- **Decision owner:** Product owner

## Context

NutriScan's core workflow depends on taking or selecting a food photograph, reviewing recognized
items and portions, calculating nutrition, and keeping local meal history. The approved product
stack already assigns this experience to React Native and Expo on Android and iOS.

A separate desktop web product would duplicate workflows, increase testing and accessibility scope,
and create pressure for account synchronization that V1 explicitly does not require.

## Decision

- `mobile/` owns the complete NutriScan application.
- `frontend/` is a desktop-friendly public landing page only.
- `backend/` provides the mobile-facing FastAPI interface and contains no web presentation code.

The landing page may explain the product, supported platforms, privacy, and availability. It does
not include scanning, food review, nutrition results, meal history, authentication, or a dashboard.

## Consequences

- Product engineering and testing stay focused on the camera-first mobile experience.
- The landing page can remain small and independently deployable.
- V1 does not need cross-device accounts or synchronization merely to support a desktop client.
- A future desktop product requires new evidence and a superseding ADR; it must not emerge by
  gradually moving mobile features into `frontend/`.

## Current gate

This decision permits directory placeholders only. Mobile and landing-page implementation remains
blocked until the vision-model selection gate passes.
