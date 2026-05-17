# Phase 12 Bootstrap Lane Contract

This note records the narrow Phase 12 bootstrap contract that current `master`
actually runs in `.github/workflows/zigux-bootstrap.yml`.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- current workflow evidence starts with `Compile current scripts`
- current Phase 12 bootstrap evidence is limited to `Self-test current Phase 12 build-only checker`
- the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- the current workflow ends the Phase 12 bootstrap slice at `Check current docs-root sanity markers`
- `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence
- until the workflow widens again, Lane 05 should keep reminder notes and small fail-closed checks aligned to this smaller sanity lane instead of treating the broader Phase 12 packet as shipped bootstrap behavior

## Next Bounded Step

If later Lane 05 work expands the workflow again, update this note and its
checker in the same change so the bootstrap contract stays exact.
