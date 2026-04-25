# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_SLICE=freeze-map-governance`
- scope: the live freeze map, a dedicated Phase 15 manifest and test gate, the shared Phase 15 build wiring, and this lane note
- survey provenance captured against verified `master` head `07d53ee63ae7cb8d148ca38b93e7e7a6d867603c`
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation. The live repo already had the first ingredient, `Documentation/zigux/freeze-map.md`, but it only listed anchors and a short policy block. It did not yet say how the lists may change, what every freeze-map lane must declare, or what blocks a freeze-in-C anchor from turning into a direct Zigux port claim.

That gap matters because the live repo now carries real Phase 14 boundary surveys for `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c`. Without a stronger Phase 15 governance rule, those surveys stay reviewable but the repo still lacks a clean product answer to the question "what would have to be true before one of these anchors leaves the freeze map?"

The honest bounded step is therefore to strengthen the freeze map itself and make the governance rule testable. This lane does not try to land a full Architecture Council process or a parity scorecard system in one pass. It records the gating rule that future Phase 15 work must respect.

## Landed governance rules

- changes to the freeze or study lists now require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in a reviewable record
- direct Zig bridge or port claims for a freeze-in-C anchor now stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- the stay-in-C policy now says the C implementation remains the product source of truth, and that ambiguous validation must keep the code in C with an explicit blocker

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-doc`
- landed `phase15-freeze-map-governance-note`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- ready-next `phase15-parity-scorecard-followup`

This keeps the lane tight: Zigux now has a reviewable and runnable governance rule for the freeze map, but it still does not pretend the broader Phase 15 parity scorecard or council workflow is complete.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- a full parity scorecard document or scoring harness
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Stay in the Phase 15 governance lane and add one bounded parity scorecard starter next so the freeze map can point at a concrete review artifact before any anchor status changes are proposed.
