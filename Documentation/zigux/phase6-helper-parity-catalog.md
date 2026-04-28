# Phase 6 Helper Parity Catalog

This note records the current shared Phase 6 leaf-helper evidence bundle at the inspected `master` tip when this catalog was refreshed.

- verified head: `be98ef3fc9c0ec48c80c82a4d7614288c2ba1b68`

## Scope

The current Phase 6 helper-parity packet is intentionally limited to the four roadmap-backed leaf helpers:

- `lib/base64.zig`
- `lib/bsearch.zig`
- `lib/checksum.zig`
- `lib/hexdump.zig`

The shared replay and gating surface for that packet is:

- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`
- `scripts/zigux/validate-phase6.py`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

This shared catalog exists so reviewers can confirm, in one place, that the roadmap-backed Phase 6 packet still stops at the four leaf helpers and that the docs, validator, workflow, and test entrypoints all describe the same shipped surface.

## Current helper evidence

### base64

- helper: `lib/base64.zig`
- tests: `zigux/tests/phase6_base64.zig`
- perf: `zigux/tests/phase6_base64_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- parity spot check: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- parity runner: `zigux/tests/phase6_base64_c_parity.zig`
- C harness: `zigux/tests/fixtures/phase6_base64_c_harness.c`
- slice note: `Documentation/zigux/phase6-base64-slice.md`

### bsearch

- helper: `lib/bsearch.zig`
- tests: `zigux/tests/phase6_bsearch.zig`
- perf: `zigux/tests/phase6_bsearch_perf.zig`
- external parity: `scripts/zigux/check-phase6-bsearch-c-parity.py`
- fixtures: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`

### checksum

- helper: `lib/checksum.zig`
- tests: `zigux/tests/phase6_checksum.zig`
- perf: `zigux/tests/phase6_checksum_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`

### hexdump

- helper: `lib/hexdump.zig`
- tests: `zigux/tests/phase6_hexdump.zig`
- perf: `zigux/tests/phase6_hexdump_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`

## Review posture

- `make -C zigux phase6-validate` is the fail-fast shared catalog gate.
- `make -C zigux phase6` replays the bundled Phase 6 helper tests together.
- The per-helper perf targets stay reviewable only through this same bounded packet; do not treat one helper-local perf harness as closure for the whole tranche.
- Reopen this catalog only when the shipped helper inventory, test labels, fixture modules, perf entrypoints, or slice-note ownership changes.
