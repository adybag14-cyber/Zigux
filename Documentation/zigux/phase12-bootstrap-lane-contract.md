# Phase 12 Bootstrap Lane Contract

This note records the current Lane 05 bootstrap viability reading on `master`
without reopening the workflow-file packet itself.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the live bootstrap workflow still keeps exact-head visibility through unfiltered `push` coverage for `master`, path-filtered `pull_request` coverage, and `workflow_dispatch`
- the same live workflow now narrows its Phase 12 bootstrap evidence to `Run current Phase 12 throughput-parity anchor` with `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig`
- current `master` still materializes `phase12-smoke`, `phase12-test`, and `phase12` in `zigux/Makefile`, but `.github/workflows/zigux-bootstrap.yml` no longer calls those shared routes
- the older support-bundle sequence `Self-test Phase 12 build-only surface checker`, `Check Phase 12 build-only surface`, `Self-test Phase 12 release-readiness packet checker`, `Validate Phase 12 degraded-workflow bundle`, `Check Phase 12 release-readiness packet`, `Run focused Phase 12 smoke shard`, and `Run Phase 12 complex driver tests` is not shipped on current `master`
- the older Phase 13 through Phase 15 release-discipline route sequence is also no longer shipped on current `master`
- `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` still belong only to open Lane 05 review branches, not current `master`
- until same-lane work restacks a fresh workflow packet, the honest Lane 05 contract is that current `master` measures Phase 12 bootstrap viability only through the direct throughput anchor plus the surviving trigger and concurrency envelope

## Next Bounded Step

If Lane 05 reopens the workflow file, the next honest move is to decide whether
to keep the narrower throughput-parity anchor or to restore a current-master
Phase 12 support bundle before widening any adjacent reminder surfaces.
