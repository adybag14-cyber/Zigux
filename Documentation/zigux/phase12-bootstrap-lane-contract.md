# Phase 12 Bootstrap Lane Contract

This note records the shipped Lane 05 bootstrap posture on current `master`
without reopening the live workflow file in the same change.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current shipped bootstrap lane still declares unfiltered `push` coverage for `master`
- the current shipped bootstrap lane still keeps path-filtered `pull_request` coverage for the Zigux-owned lane files
- the open trigger-gap investigation is therefore a runtime attachment problem rather than a missing trigger stanza in the committed workflow file
- the current shipped bootstrap lane still compiles `scripts/zigux/*.py` before any lane checks run
- the current shipped lane still keeps the pinned Zig archive check and the Phase 11 build-inventory plus matrix-gap survey checks
- the current shipped Phase 12 slice still includes the build-only surface pair, the release-readiness pair, `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- the current shipped lane still runs `make -C zigux phase8-validate` and the focused Phase 8 libbpf segment survey after the Phase 12 complex driver tests
- the current shipped bootstrap lane still ends with the inline `Check current docs-root sanity markers` block
- the inline docs-root sanity block still checks `Documentation/zigux/README.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `zigux/tests/README.md`, and `scripts/zigux/check-build-only-phase12-surface.py`
- dedicated `check-phase12-bootstrap-docs-sanity.py` and `check-phase12-bootstrap-lane-shape.py` guards remain review-only Lane 05 work, not shipped `master` behavior

## Next Bounded Step

If the shipped workflow replaces the inline docs-root sanity block later, refresh
this note and its checker in the same lane change.
