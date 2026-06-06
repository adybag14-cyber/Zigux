# Backup Audit B Phase 1 Guidance Correction

Date: 2026-06-06

This note records the narrow truthfulness correction from the Backup audit B progress-debugger pass. It should be used by future scheduled runs before following older Phase 1 missing-surface wording in the shared reminder indexes.

## Current Authenticated Readback

The following paths are directly readable on current `master` and must not be treated as missing current-master evidence:

- `scripts/zigux/install-zig.py`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`

The following paths still returned 404 during this audit and remain historical or broader closure-stack vocabulary until a later fresh reread proves otherwise:

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/check-phase1-installer-review-surfaces.py`
- `scripts/zigux/check-phase1-installer-companion-checks.py`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`

## Correction

Older reminder text that groups `scripts/zigux/install-zig.py`, `zigux/tests/phase1_bench.zig`, and `zigux/tests/fixtures/phase1_bench_expectations.json` with missing Phase 1 surfaces is stale. Future runs should split that guidance:

- keep the installer path as returned current repo evidence through the Phase 2 toolchain and bootstrap packet
- keep the Phase 1 bench source and expectation fixture as returned broader closure companions
- keep `validate-phase1.py`, the old installer-review checkers, and the C harness in the missing or historical bucket until fresh current-master evidence changes that state

## Follow-Up

The larger reminder surfaces should be cleaned in place when a run can safely update their full file bodies:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- any companion checker that still asserts the older combined missing list

This note is intentionally narrow so it corrects the stale operational guidance without rewriting the large reminder indexes through a whole-file replacement path.