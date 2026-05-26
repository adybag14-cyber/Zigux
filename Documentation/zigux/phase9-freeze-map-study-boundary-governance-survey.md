# Phase 9 Freeze-Map Study-Boundary Governance Survey

## Status

- `PHASE9_STATUS=freeze_boundary_governance_survey_landed`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SLICE=freeze-map-study-boundary-governance-survey`
- `PHASE9_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-26`
- role: record the roadmap-versus-repo comparison for the shared Phase 9 runtime-pilot freeze-boundary packet without widening into Phase 15 ownership or new runtime behavior claims

## Why this note exists

Phase 9 is a runtime-pilot tranche, not a license to treat deeper study-only anchors as ready for delivery.

The roadmap explicitly keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in a boundary-study posture first. The live Phase 9 reminder packet already routes those anchors back through the freeze map and the Phase 15 study-only accounting note, but the repo did not yet have one dedicated survey note for this exact Phase 9 governance comparison.

This note closes that evidence gap without reopening broader runtime-loader, publication, install-root, or deep-core status-change work.

## Roadmap basis

- Phase 9 remains the runtime-pilot module tranche
- runtime pilot evidence belongs in bounded `zigux/tests/runtime_*` and `samples/zigux/runtime_*` surfaces
- deep-core freeze still applies outside those runtime-pilot bounds
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors before any direct port decision

## Current repo reality

Current `master` already keeps the Phase 9 study-boundary packet explicit through:

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
- `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`

Those surfaces already do the important governance work:

- they keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as study-only boundary context rather than runtime-substrate readiness proof
- they keep the shipped trace-events packet distinct from the narrower shared runtime-loader shard, the bounded runtime bitmap reminder packet, and the family-local runtime kretprobe pilot packet
- they keep the Phase 9 build and Makefile routes framed as bounded rerun vocabulary rather than proof that blocked publication or install-root boundaries are complete

## Governance gap assessment

No roadmap-level study-boundary break is visible on current `master`.

The active governance risk is narrower:

- reminder-surface drift could let a future Phase 9 note summarize the study-only anchors without routing back through the freeze map owner notes
- a future shared reminder surface could overclaim runtime-substrate readiness from the bounded loader, bitmap, or kretprobe packets
- a future rerun route summary could be mistaken for publication or install-root closure if the Phase 9 packet loses its current non-owner wording

Current repo reality does not show those failures now. The existing reminder packet and checker-backed enforcement surfaces still match the roadmap-backed study-only posture.

## Current lane decision

- keep the Phase 9 lane in maintenance mode for freeze-boundary governance
- do not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence
- treat any future work here as reminder-surface truthfulness maintenance first

## Next bounded step

Reopen this lane only if one of these becomes true:

- `Documentation/zigux/freeze-map.md` changes the study-only anchor set
- `Documentation/zigux/phase15-study-only-anchor-accounting.md` changes the two-anchor inventory or posture
- one Phase 9 reminder surface stops routing study-only summaries back through the owner notes
- one Phase 9 reminder surface starts presenting the bounded loader, bitmap, or kretprobe packet as proof of deeper runtime-substrate, publication, or install-root completion
