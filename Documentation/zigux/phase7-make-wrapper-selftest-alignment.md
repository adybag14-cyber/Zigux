# Phase 7 Make-Wrapper Self-Test Alignment

This document records the bounded shared Phase 7 integration-governance surface around the make-wrapper self-test route.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=phase7-make-wrapper-selftest-alignment`
- `PHASE7_LANE_KEY=P7-Y05`
- scope: shared validator and make-wrapper self-test alignment only
- lane state: dedicated alignment checker, shared validator route, and reviewer-facing summary reminders landed; parked unless the shared Phase 7 validator, Makefile, bootstrap workflow, docs-root, review-checklist, scripts-root, tests-root, or sample-root summaries drift away from the same self-test packet
- product boundary:
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/validate-phase7.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `samples/zigux/README.md`

## Why this note exists

Phase 7 is already parked as a shared validator-first helper bundle, but the make-wrapper self-test surface is a shared route rather than a helper-owned packet. This note keeps that shared route explicit so the self-test stays centralized in the make path instead of drifting into ad hoc workflow calls or disappearing from the shared validator.

## Current shared contract

- `scripts/zigux/check-phase7-make-wrapper.py --self-test` stays owned by `zigux/Makefile` rather than a direct workflow-only invocation
- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py` keeps `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/validate-phase7.py`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the no-sample reminder in `samples/zigux/README.md` aligned around that centralized self-test path
- `scripts/zigux/validate-phase7.py` keeps this shared governance note inside the parked Phase 7 validator-first packet
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `samples/zigux/README.md` remain the shared reviewer-facing summaries that should name this alignment note when they describe the parked Phase 7 validator-first and no-sample boundary packet, so the make-wrapper self-test route does not disappear behind helper-local proofs alone
- `make -C zigux phase7-validate` and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface

## Non-goals

- this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`
- this note does not add a new per-slice CI step or a broader `phase7_build_inventory` packet

## Next bounded step

Fresh repo inspection now shows the older make-wrapper-alignment follow-through is complete on `master`: the dedicated alignment checker and shared validator both fail closed if `samples/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` drops this dedicated alignment note while the shared make-wrapper control surface remains part of the parked Phase 7 packet.

Keep this specific shared-control lane parked unless a new tiny same-lane checker, note, workflow, Makefile, or sample-root drift appears here.

The broader Phase 7 packet still carries one separate validator-only follow-through outside this note: live `scripts/zigux/validate-phase7.py` does not yet exact-count the newly explicit `Documentation/zigux/review-checklist.md` markers in `Documentation/zigux/phase7-string-helpers-slice.md` and `Documentation/zigux/phase7-rbtree-slice.md`, so that remaining hardening should land as its own one-file validator update rather than being folded back into this parked make-wrapper alignment lane.
