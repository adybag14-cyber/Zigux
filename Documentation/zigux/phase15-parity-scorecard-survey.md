# Phase 15 Parity Scorecard Survey

This document records the bounded Phase 15 roadmap-facing survey for the live parity-accounting packet on `master`.

## Status

- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_STATUS=parity_scorecard_survey_landed`
- `PHASE15_SLICE=parity-roadmap-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- scope: one survey-grade note that compares the roadmap's parity-scorecard requirement against the live scorecard note, machine-readable JSON, and dedicated Zig guard without widening into new deep-core implementation or shared-summary follow-through
- survey rechecked against current `master` on 2026-05-19; the dedicated parity-scorecard packet now carries dated readback marker `current-master-readback-2026-05-19`
- product boundary:
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `Documentation/zigux/phase15-parity-scorecard-survey.md`

## Why this survey exists

The roadmap's Phase 15 packet requires a parity scorecard so the freeze-in-C anchors stay reviewable through explicit ownership, blocker posture, and replay evidence.

The honest same-lane question on current `master` is no longer whether Zigux lacks a parity scorecard. It is whether the roadmap-facing survey still describes the live parity-accounting packet truthfully after the dedicated scorecard note, JSON companion, and Zig guard all landed and were later refreshed.

## Current master readback

The 2026-05-19 reread shows these dedicated parity-scorecard surfaces present on current `master`:

- `Documentation/zigux/phase15-parity-scorecard.md`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`

The dedicated scorecard note and JSON still agree on the core packet shape:

- lane key: `P15-L03`
- slice: `parity-scorecard-baseline`
- provenance mode: `dated_master_readback`
- surveyed commit marker: `current-master-readback-2026-05-19`
- posture: `blocked_posture_accounting_not_port_readiness`

The live machine-readable metrics still cover:

- active freeze-in-C anchor count: `4`
- blocked status-change anchor count: `4`
- anchors blocked entirely within Phase 15 governance evidence: `2`
- Phase 14 coupled blocker anchor count: `2`
- anchors still blocked on prior-phase bridge evidence: `2`
- study-only anchors tracked outside the scorecard: `2`
- Architecture Council approvals recorded for status change: `0`

The live anchor inventory remains:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

Each anchor still carries explicit lane owner, phase, current status bucket, required approver set, validation gate summary, rollback owner, current blocker, evidence-archive path, benchmark-notes status, replay command, and next honest posture.

The exact handoff reread also shows one remaining parity-packet truthfulness drift on current `master`:

- `Documentation/zigux/phase15-parity-scorecard.md` now says the broader validator-first and shared-build reminder routes through `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15{,-validate,-test}` are shipped reminder-route evidence on current `master`
- `zigux/tests/phase15_parity_scorecard.zig` still expects the narrower wording that treats those broader validator-first and shared-build routes as repo-reality gap vocabulary rather than shipped evidence
- `Documentation/zigux/phase15-governance-lane-sequencing.md` still records `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the lane-owner companion as missing broader Phase 15 companions on current `master`
- direct current-`master` readback on 2026-05-19 still returned missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, so the dedicated scorecard note is the stale surface, not the narrower replay guard

## Exact checks

The exact 2026-05-19 checks for this bounded handoff step were:

- read `Documentation/zigux/phase15-parity-scorecard.md` and confirmed its status block now advertises `PHASE15_LANE_KEY=P15-L03`, `PHASE15_PROVENANCE_MODE=dated_master_readback`, and `current-master-readback-2026-05-19`
- read `zigux/tests/phase15_parity_scorecard.json` and confirmed the same lane key, slice, dated-readback marker, posture role, four-anchor inventory, and `0` Architecture Council approvals
- read `zigux/tests/phase15_parity_scorecard.zig` and confirmed the dedicated Zig guard still checks for `P15-L03`, `current-master-readback-2026-05-19`, the same aggregate metrics, and the narrower reminder-route sentence that keeps `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15*` routes in repo-reality-gap wording
- read `Documentation/zigux/phase15-governance-lane-sequencing.md` and confirmed the broader governance packet still lists `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` as missing current-`master` companions
- attempted direct current-`master` readback for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`; both returned missing on 2026-05-19

## Current roadmap posture

The roadmap-required parity scorecard packet is still substantively present on current `master`.

The dedicated scorecard note, machine-readable JSON companion, and dedicated Zig guard are all landed, so the core parity-tracking requirement named by the roadmap remains satisfied inside the Phase 15 governance packet.

The remaining same-lane drift is now narrower than a missing-scorecard problem:

- this survey note previously said the dedicated parity-scorecard packet was fully aligned across the note, JSON companion, and dedicated Zig guard
- exact current-`master` reread now shows that the dedicated scorecard note overstates broader validator-first and shared-build route materialization, while the JSON companion and dedicated Zig guard still keep the blocked-posture packet honest

That means the survey-local truthfulness gap is no longer provenance lag. It is an exact handoff mismatch between the dedicated scorecard note and the narrower parity replay expectations.

## Honest current posture

The honest bounded Phase 15 statement on current `master` is:

- the roadmap-required parity scorecard is landed as a note plus machine-readable JSON plus dedicated Zig guard
- no Architecture Council approval is recorded for any freeze-map status change
- all four freeze-in-C anchors remain blocked from a direct Zigux port claim
- the dedicated parity-scorecard packet now belongs to `P15-L03`
- the current same-family drift is the dedicated scorecard note's broader reminder-route wording, not the absence of the scorecard packet itself
- this survey lane should stay parked after recording that exact mismatch unless a fresh reread shows either the dedicated note has been refreshed or the broader missing routes have actually returned

## Recorded gaps

The current lane state is:

- landed `phase15-parity-scorecard-roadmap-requirement`
- landed `phase15-parity-scorecard-doc`
- landed `phase15-parity-scorecard-json`
- landed `phase15-parity-scorecard-zig-guard`
- landed `phase15-parity-scorecard-survey-exact-handoff-readback`
- blocked `phase15-parity-scorecard-broader-route-wording-drift`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane narrow.

The next truthful follow-through for broader reminder-route wording belongs to the dedicated parity-scorecard owner packet, not to this roadmap-facing survey.

## Non-goals

This survey does not claim:

- any Architecture Council approval for a freeze-map status change
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge, wrapper, or direct port starter
- any shared Phase 15 reminder cleanup outside this survey note

## Next bounded step

Keep `P15-L09` parked after recording this exact mismatch unless a fresh reread shows one of two changes:

- `Documentation/zigux/phase15-parity-scorecard.md` is refreshed so its broader reminder-route wording matches the narrower dedicated Zig guard and the governance sequencing note again
- `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15{,-validate,-test}` routes actually return on current `master`

If it reopens, compare the roadmap, this survey note, `Documentation/zigux/phase15-parity-scorecard.md`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, and `Documentation/zigux/phase15-governance-lane-sequencing.md` together before touching any neighboring Phase 15 packet.
