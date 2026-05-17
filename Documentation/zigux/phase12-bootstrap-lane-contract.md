# Phase 12 Bootstrap Lane Contract

This note records the current Phase 12 portion of the bootstrap workflow without
rewriting the broader reminder packet or the in-flight workflow restack branch.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current bootstrap workflow still begins with `Compile current scripts`
- the current Phase 12 slice is a tail contract, not the whole workflow
- current upstream bootstrap steps ahead of that tail include the current Zig toolchain checker pair, the Phase 2 kconfig, kbuild, and toolchain-pinning pairs, the Phase 1 direct-owner and string-review pairs plus the bench and shared-reminder checks, and the Phase 4 repo-reality, reversible-delivery, and tests-readme pairs
- the current Phase 12 bootstrap tail is limited to `Self-test current Phase 12 build-only checker` followed by `Check current docs-root sanity markers`
- the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence
- until the workflow widens again, Lane 05 should keep reminder notes and fail-closed checks aligned to this smaller Phase 12 tail instead of treating the broader Phase 12 packet as shipped bootstrap behavior

## Next Bounded Step

If later Lane 05 work lands the dedicated bootstrap-lane-shape or docs-sanity
checkers in the workflow, refresh this note and its checker in the same change.
