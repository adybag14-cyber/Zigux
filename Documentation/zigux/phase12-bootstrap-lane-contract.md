# Phase 12 Bootstrap Lane Contract

This note records the current Lane 05 bootstrap posture on shipped `master`
without reopening the live workflow file in the same change.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the shipped bootstrap lane still compiles `scripts/zigux/*.py` before any workflow guards run
- the shipped lane still keeps the Zig toolchain self-test, policy, and pinned-archive checks together at the top of the workflow
- the shipped lane still keeps the current Phase 2 kconfig, tests README, cross-selftest, toolchain-pinning, toolchain pin-scope, required-make-routes, shared-reminder, and `validate-phase2.py` packet intact
- the shipped lane still keeps the current Phase 1 direct-owner, string-review, bench self-test, shared-reminder, and shared tests-root smoke packet intact
- the shipped lane still keeps the current Phase 4 repo-reality, reversible-delivery, and tests README packet intact
- the shipped lane still keeps the current Phase 7 shared-control gap packet intact
- the shipped lane still keeps the current Phase 10 bootstrap-route pair plus `make -C zigux phase10-validate` and `make -C zigux phase10-test`
- the shipped lane currently ends with the Phase 11 HVC cleanup current-head pair
- no shipped Phase 12 or Phase 8 tail remains on current `master`
- no shipped inline `Check current docs-root sanity markers` block remains on current `master`
- review-only Lane 05 packets such as `check-phase12-bootstrap-docs-sanity.py`, `check-phase12-bootstrap-lane-shape.py`, and this contract checker are still unmerged on current `master`

## Next Bounded Step

If the shipped workflow grows a new Lane 05 tail later, refresh this note and
its checker in the same bounded lane change.
