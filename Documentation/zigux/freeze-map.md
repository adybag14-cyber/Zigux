# Zigux Freeze Map

This file records code that should not move into active Zigux delivery without an explicit Architecture Council decision.

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- changes to either list require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in the reviewable record for that lane
- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and keep the decision record ID, requested decision bucket, evidence archive path, latest blocker disposition, benchmark notes, replay command, retained discussion state, reopen triggers, parity scorecard link or blocker record, and indefinite-C policy link or non-applicability note explicit beside those minimum lane fields
- direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change

## Stay-In-C Policy
- the existing C implementation remains the product source of truth for every freeze-in-C anchor
- allowed near-term Zigux work on those anchors is limited to survey notes, boundary manifests, validation gates, and explicit non-goal records
- wrapper-first or helper-first experiments may continue only for study-only anchors, and they still must keep scheduler, MM, RCU, skbuff, and other deep-core ownership explicit
- the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying scheduler-facing substrate closure or a freeze-map status change
- if validation is incomplete, contradictory, or too weak to justify a status change, keep the code in C and record the blocker
- closing a freeze-in-C review without a status change must retain the blocker, record the closeout as `retired_from_active_discussion`, and keep the reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Policy
- deep-core files do not become sprint targets by enthusiasm alone
- research is allowed
- product commitments require explicit gates, validation, and ownership
- if evidence is not overwhelming, keep the code in C and document why