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
- any `kernel/workqueue.c`-adjacent Phase 9 runtime-loader review must keep `Documentation/zigux/phase9-runtime-loader-substrate-plan.md` named beside `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-loader-substrate-plan.py`, `zigux/kernel/runtime_loader.zig`, the landed `samples/zigux/runtime_{atomic64,bitmap,kretprobe}_loader.zig` plans, the shipped sample-only `samples/zigux/runtime_trace_events_loader.zig` scaffold, and `zigux/tests/phase9_build.zig` so the shared loader-stage vocabulary stays in the same reviewable ownership packet while the fourth trace-events scaffold remains visibly blocked beside the study-only anchors
- any `kernel/trace/ring_buffer.c`-adjacent Phase 9 runtime trace-events review must keep `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_manifest.json`, `zigux/tests/runtime_trace_events_survey.zig`, and `zigux/tests/phase9_build.zig` named together so the study-only trace-core boundary, the bounded blocked loader scaffold, the no-status-change posture, and the Architecture Council reopen rule stay in one reviewable packet
- direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- any freeze-map review packet that reopens a blocked anchor must state the rollback threshold that forces the anchor back to its blocked freeze posture if the decision record, scorecard evidence, benchmark notes, replay command, blocker disposition, or rollback owner stops being explicit
- any freeze-map review packet that reopens a blocked anchor must also say plainly that the existing C implementation remains the product source of truth unless the Architecture Council approves the requested status change

## Stay-In-C Policy
- the existing C implementation remains the product source of truth for every freeze-in-C anchor
- allowed near-term Zigux work on those anchors is limited to survey notes, boundary manifests, validation gates, and explicit non-goal records
- wrapper-first or helper-first experiments may continue only for study-only anchors, and they still must keep scheduler, MM, RCU, skbuff, and other deep-core ownership explicit
- if validation is incomplete, contradictory, or too weak to justify a status change, keep the code in C and record the blocker
- closing a freeze-in-C review without a status change must retain the blocker, record the closeout as `retired_from_active_discussion`, and keep the reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Policy
- deep-core files do not become sprint targets by enthusiasm alone
- research is allowed
- product commitments require explicit gates, validation, and ownership
- if evidence is not overwhelming, keep the code in C and document why
