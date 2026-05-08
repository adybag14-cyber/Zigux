# Phase 7 Make-Wrapper Self-Test Alignment

This document records the bounded shared Phase 7 integration-governance surface around the make-wrapper self-test route.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=phase7-make-wrapper-selftest-alignment`
- `PHASE7_LANE_KEY=P7-Y05`
- scope: shared validator and make-wrapper self-test alignment only
- lane state: dedicated alignment checker and shared validator route landed; parked unless the shared Phase 7 validator, Makefile, or bootstrap workflow drifts away from the same self-test packet
- product boundary:
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/validate-phase7.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why this note exists

Phase 7 is already parked as a shared validator-first helper bundle, but the make-wrapper self-test surface is a shared route rather than a helper-owned packet. This note keeps that shared route explicit so the self-test stays centralized in the make path instead of drifting into ad hoc workflow calls or disappearing from the shared validator.

## Current shared contract

- `scripts/zigux/check-phase7-make-wrapper.py --self-test` stays owned by `zigux/Makefile` rather than a direct workflow-only invocation
- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py` keeps `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around that centralized self-test path
- `scripts/zigux/validate-phase7.py` keeps this shared governance note inside the parked Phase 7 validator-first packet
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` remain the shared reviewer-facing summaries that should name this alignment note when they describe the parked Phase 7 validator-first packet, so the make-wrapper self-test route does not disappear behind helper-local proofs alone
- `make -C zigux phase7-validate` and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface

## Non-goals

- this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`
- this note does not add a new per-slice CI step or a broader `phase7_build_inventory` packet

## Next bounded step

Fresh repo inspection still shows the older docs-root, tests-root, samples-root, and scripts-root make-route follow-through is already complete: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and the dedicated alignment checker already keep this note plus the full `make -C zigux phase7-validate` and `make -C zigux phase7` review route explicit inside the parked Phase 7 packet. The next honest same-lane gap is now validator-local instead: `scripts/zigux/validate-phase7.py` still does not fail closed if `Documentation/zigux/README.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` ever drops this dedicated alignment note while the shared make-wrapper control surface remains part of the parked Phase 7 packet. Prefer that one-file validator exact-count repair before reopening helper code, fixture churn, or broader README wording.
