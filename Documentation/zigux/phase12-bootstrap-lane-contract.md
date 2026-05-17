# Phase 12 Bootstrap Lane Contract

This note records the current Phase 12 portion of the bootstrap workflow without
rewriting the broader reminder packet or reopening the live workflow file in this
lane.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current bootstrap workflow still begins with `Compile current scripts`
- the current Phase 12 slice is a tail contract, not the whole workflow
- current upstream bootstrap steps ahead of that tail include the current Zig toolchain checker pair, the Phase 2 kconfig, kbuild, and toolchain-pinning pairs, the Phase 1 direct-owner and string-review pairs plus the bench and shared-reminder checks, the Phase 4 repo-reality, reversible-delivery, and tests-readme pairs, and the Phase 7 shared-control gap pair
- the current Phase 12 bootstrap tail is limited to `Self-test current Phase 12 build-only checker` followed by `Check current docs-root sanity markers`
- the current workflow reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` are broader Phase 12 routes, not current bootstrap-lane evidence
- `Check current Phase 12 build-only surface`, `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` belong to the older branch-only Lane 05 packet, not current `master`
- until the workflow widens again, Lane 05 should keep reminder notes and fail-closed checks aligned to this smaller Phase 12 tail instead of treating the broader Phase 12 packet or the older branch-only lane packet as shipped bootstrap behavior

## Next Bounded Step

If later Lane 05 work changes the live bootstrap tail again, refresh this note
and its checker in the same change.
