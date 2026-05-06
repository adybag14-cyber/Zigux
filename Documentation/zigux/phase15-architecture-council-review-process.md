# Phase 15 Architecture Council Review Process Survey

This document records the bounded Phase 15 governance lane around the Architecture Council review-process gap named in the roadmap.

## Status

- `PHASE15_STATUS=review_process_slice_landed`
- `PHASE15_SLICE=architecture-council-review-process-reopen-trigger-catalog`
- `PHASE15_LANE_KEY=P15-L08`
- scope: one review-process note, one dedicated manifest and Zig test, the focused lane-owner vocabulary alignment replay already shipped in the shared Phase 15 build, the shared Phase 15 build wiring, and a small review-checklist update that now also names the retained stay-in-C closeout state and reopen triggers
- survey provenance refreshed against verified `master` head `3eac40e856ac7673f705447a1d6025f3d0193b5e`
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `zigux/tests/phase15_architecture_council_review_process_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `zigux/tests/phase15_architecture_council_review_process.zig`
  - `zigux/tests/phase15_handoff_next_steps.zig`
  - `zigux/tests/phase15_indefinite_c_policy.json`
  - `zigux/tests/phase15_indefinite_c_policy.zig`
  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  - `zigux/tests/phase15_readiness_gate.zig`
  - `zigux/tests/phase15_build.zig`

## Why this slice exists

The roadmap's Phase 15 requirements include an Architecture Council review process, a parity scorecard, and the policy for code that remains in C indefinitely. Current `master` now carries the freeze map, stay-in-C governance language, and a landed parity-scorecard baseline, but this review-process note is still the reviewable record that says when the Architecture Council must be engaged, what evidence a request must carry, and what bounded outcomes are allowed.

That missing process leaves a governance gap between the roadmap and the live repo. Without it, a future patch can mention the Architecture Council in principle while still leaving reviewers to guess what packet a status-change request needs and which decisions are legitimate inside the current mixed-language product plan.

The honest bounded step is to land a survey-grade review-process note that turns the roadmap requirement into a concrete review artifact without pretending the council already has a full roster, cadence, or automation surface. The shared Phase 15 build now also carries a focused lane-owner vocabulary alignment replay, so this parked packet should name that replay directly instead of understating the current governance boundary.

## Trigger Conditions

The Architecture Council review process must be invoked when a lane proposes any of the following:

- a change to the freeze-in-C list or the study-only list in `Documentation/zigux/freeze-map.md`
- a status-bucket change for a freeze-map anchor, including any request to move from `freeze in C initially` toward a direct Zigux port claim
- a claim that a deep-core boundary study is now ready for bounded dual implementation
- contradictory validation results that need a written decision about whether the code stays in C with a blocker or advances to another bounded status

## Required Review Packet

Every Architecture Council request in this lane family must carry:

- the exact Linux anchor path and current roadmap phase
- the current status bucket and the requested decision bucket
- the decision record ID for the specific review being requested
- the named owner for the lane and the rollback owner
- the validation gate summary with links to the live evidence
- the evidence archive path that preserves linked surveys, blocker follow-ups, benchmark notes, and replay commands
- the latest blocker disposition saying whether the anchor remains blocked, is ready for narrower follow-up, or has been rejected for status change
- the current benchmark-notes status so reviewers can see whether performance evidence exists yet
- the replay command reviewers should run before trusting the current packet
- the rollback threshold that says when the packet must return to an explicit stay-in-C blocker instead of treating weak or contradictory evidence as forward progress
- the retained discussion state that will be recorded if the review closes with a stay-in-C outcome
- the reopen triggers that cite one or more catalog items naming which evidence changes can reopen the discussion later without implying approval
- a parity scorecard link, or an explicit blocker record saying why the scorecard is not ready yet
- the indefinite-C policy link for any request that would keep the anchor in C, or an explicit non-applicability note when the request is asking for another decision bucket
- explicit non-goals so the request does not quietly widen into deep-core delivery
- the written rationale for why the current product state needs council attention now

## Decision Buckets

The bounded outcomes for this review process are:

- `keep_in_c`: the existing C implementation remains the product source of truth and the blocker stays recorded
- `study_only_followup`: a boundary-study lane may continue, but no direct Zigux ownership claim is approved
- `bounded_dual_implementation`: a tightly scoped wrapper-first or dual-implementation follow-up is allowed with named validation and rollback gates
- `defer_or_reject`: the request is not approved and the lane must narrow or stop

## Recordkeeping Rules

- every decision must leave a written rationale in a reviewable artifact
- the lane note must record the current status bucket, the chosen decision bucket, the decision record ID, the owner, the validation gate, the evidence archive path, the latest blocker disposition, the current benchmark-notes status, the replay command, the rollback threshold, the retained discussion state, the reopen triggers, and the rollback owner
- if the council keeps the code in C, the blocker must remain explicit rather than disappearing into prose
- if the council keeps the code in C and closes active discussion, the decision record ID, evidence archive path, latest blocker disposition, replay command, retained discussion state, and reopen triggers must remain explicit; the retained discussion state must be `retired_from_active_discussion`; and the reopen triggers must stay attached to the evidence archive using one or more catalog items
- if the parity scorecard is missing, the record must say that clearly instead of implying silent approval

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for a retired stay-in-C packet is:

- `narrower_followup_answers_blocker`: a narrower seam inventory or follow-up now answers the latest blocker disposition without widening the approved boundary
- `evidence_packet_stale_or_contradictory`: linked validation, benchmark, survey, or blocker evidence has become stale or contradictory enough that the closed packet no longer stands on its own
- `ownership_or_validation_changed`: rollback ownership, lane ownership, or validation gates changed enough to invalidate the closed stay-in-C packet

Every retained stay-in-C closeout must cite at least one of these catalog items in its evidence archive so the scorecard, review-process note, and future exception records keep the same reopen vocabulary.

## Current Approval Posture

- no Architecture Council approval is currently recorded for a freeze-map status change
- the current bounded evidence is the freeze map, this review-process note, the review checklist hook, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `Documentation/zigux/phase15-parity-scorecard.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the focused `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` replay already wired through the shared Phase 15 build, and the rest of the parked `phase15_freeze_map_governance`, `phase15_architecture_council_review_process`, `phase15_handoff_next_steps`, `phase15_indefinite_c_policy`, and `phase15_readiness_gate` evidence packet carried by `zigux/tests/phase15_build.zig`
- current review-process evidence is limited to named `phase`, `current status bucket`, `owner`, `rollback owner`, `validation gate summary`, `parity scorecard link or blocker record`, `indefinite-C policy link or non-applicability note`, evidence archive, blocker-disposition, benchmark-notes, replay-command, rollback-threshold, retained-discussion-state, and reopen-trigger records in the review packet plus the validator-first `make -C zigux phase15-validate` route and the anchor-specific rollback-owner records in the parity scorecard
- until both the review record and the parity scorecard say otherwise, every freeze-in-C anchor remains blocked from an approval claim

## Recorded Gaps

The current lane state is:

- landed `phase15-architecture-council-review-process-doc`
- landed `phase15-architecture-council-review-process-manifest`
- landed `phase15-architecture-council-review-process-test`
- landed `phase15-review-checklist-hook`
- landed `phase15-build-gate-review-process`
- landed `phase15-parity-scorecard-baseline`
- landed `phase15-evidence-archive-followup`
- landed `phase15-stay-in-c-retirement-rule`
- landed `phase15-reopen-trigger-catalog-followup`
- landed `phase15-roadmap-minimum-field-sync`
- landed `phase15-lane-owner-alignment-replay-visible`

This keeps the slice narrow. Zigux gains a reviewable Architecture Council process description that now points at the landed parity scorecard, aligns the required packet with the scorecard's decision-record fields, restores the explicit indefinite-C policy linkage for stay-in-C requests, keeps the rollback-threshold gate explicit when evidence is weak or contradictory, names the retained stay-in-C closeout state, standardizes the reopen-trigger catalog, states the current no-approval posture plainly, keeps the roadmap-minimum `phase`, status-bucket, and validation-gate evidence explicit in the parked packet, and makes the already-landed lane-owner vocabulary alignment replay visible inside the same governance boundary, but it still does not claim a real council roster or any change to a freeze-map anchor status.

## Non-goals

This slice does not claim:

- a full Architecture Council charter, roster, calendar, or voting system
- Architecture Council approval for any freeze-map status change
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- any new deep-core Zig bridge, wrapper, or direct port starter

## Gates

1. run the validator-first route
- `make -C zigux phase15-validate`

2. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

3. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The indefinite-C field-sync follow-up is already landed, so the next honest action is to wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice.
