# Phase 15 Study-Only Anchor Accounting

This note records the bounded Phase 15 governance view of the roadmap-backed study-only anchors that remain outside the freeze-in-C scorecard.

## Status

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_LANE_KEY=P15-L05`
- `PHASE15_SLICE=study-only-anchor-accounting`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`
- scope: keep the two roadmap-backed study-only anchors explicit beside the freeze map, the Phase 15 freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note without claiming a status-bucket review, a direct Zigux bridge, or an Architecture Council approval path
- role: reviewable accounting for anchors that the roadmap still treats as boundary-study targets first and that the current Phase 15 scorecard intentionally counts outside blocked status-change rows

## Why this slice exists

The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.

Current `master` now carries a more complete Phase 15 governance packet through the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note. Those documents already keep the study-only anchor count and the maintenance boundaries explicit, but they still treat that set as surrounding governance context rather than a direct reviewable inventory.

The honest same-lane follow-up is therefore accounting, not expansion: keep the two study-only anchors explicit in one bounded note so future maintenance reads do not have to infer them indirectly from the roadmap, the aggregate scorecard count, or the broader shared-summary packet.

This refresh closes the note's dated-readback drift. Reviewers can now read it against the current 2026-05-18 governance packet instead of reconciling it against an older study-only note by hand.

## Roadmap Basis

- `kernel/workqueue.c` remains a boundary-study target first, not a rewrite target
- `kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target
- any future Zigux work here stays wrapper-first or study-only until much stronger evidence exists
- speculative direct ports such as `kernel/workqueue_bridge.zig` or `kernel/trace/ring_buffer.zig` remain future-only and not current product claims

## Current Repo Reality

- the current Phase 15 freeze-map governance note keeps the study-only scope unchanged while staying in maintenance mode
- the current Phase 15 parity scorecard still records `study-only anchors tracked outside this scorecard: 2`
- the current Phase 15 handoff-next-steps survey keeps the same two study-only anchors parked beside the existing governance packet and reopens only if a broader reminder surface drifts
- the current Phase 15 shared-summary gap note keeps docs-root, checklist, scripts-root, tests-root, and validator-first wording drift framed as truthfulness follow-through rather than study-only status-change evidence
- this note's dated-readback marker now matches the current 2026-05-18 governance packet instead of lagging behind the already-refreshed handoff, readiness, parity, and stay-in-C companions
- no Architecture Council approval is currently recorded for a deep-core status change
- the current governance packet is still blocker-accounting and handoff truthfulness, not port-readiness

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`
- roadmap reason: boundary-study target first, not a rewrite target
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows
- next honest posture: keep it in study-only accounting until a narrower bounded seam exists and a future governance lane records why the anchor should move beyond boundary-study review

### `kernel/trace/ring_buffer.c`
- posture: `study_only`
- roadmap reason: boundary-study target first, not a rewrite target
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows
- next honest posture: keep it in study-only accounting until a narrower bounded seam exists and a future governance lane records why the anchor should move beyond boundary-study review

## Accounting Rules

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- if a future scorecard or governance note changes the reported study-only count, this note must reconcile the same anchor set directly instead of leaving the count implicit
- if the handoff-next-steps survey or shared-summary gap note changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary
- any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together

## Non-Goals

This slice does not claim:

- a direct Zigux bridge for `kernel/workqueue.c`
- a direct Zigux bridge for `kernel/trace/ring_buffer.c`
- an Architecture Council approval for any study-only anchor to leave its current posture
- a new implementation roadmap beyond current governance accounting

## Next bounded step

Keep this note parked unless the freeze map changes the study-only set, the parity scorecard changes its study-only count, the handoff or shared-summary packet drifts enough that the two-anchor inventory needs a truthfulness refresh, or a future governance lane produces a smaller reviewable seam for one of these anchors.
