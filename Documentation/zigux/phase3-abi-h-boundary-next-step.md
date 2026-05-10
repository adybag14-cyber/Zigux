# Phase 3 ABI Header Boundary Next Step

## Purpose

This note records the smallest honest follow-through when the shared Phase 3 reminders drift away from the dedicated ABI header-family packet.

## Current Lane Position

The current `master` packet already ships:
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `make -C zigux phase3-validate`

Those surfaces are enough to keep the header-family survey itself real.

## Preferred Follow-Through Order

When another same-lane repair is needed, keep the order small:
1. fix the shared wording surface that drifted
2. rerun the dedicated survey checker or its self-test route
3. avoid reopening unrelated Phase 3 helper, tests-root, or runtime-helper work in the same step

## Current Recommended Same-Lane Follow-Through

The next bounded same-lane repair after this note is to refresh `Documentation/zigux/README.md` so the broad Phase 3 summary explicitly keeps:
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`

visible beside the existing ABI bindings, export/UAPI, low-level-wrapper, policy-byte, catalog, and Linux-style `phase3-validate` reminder packet.

## Non-Goals

This note does not reopen:
- Phase 3 helper-tree expansion
- allocator, panic, atomic, barrier, or MMIO scope growth
- new tests-root inventory work
- runtime-loader or later-phase runtime pilot work