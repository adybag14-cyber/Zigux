# Phase 15 Architecture Council Review Process Survey

This document records the bounded Phase 15 governance lane around the Architecture Council review-process gap named in the roadmap.

## Status

- `PHASE15_STATUS=review_process_slice_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_SLICE=architecture-council-review-process-decision-record-template`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- scope: one review-process note, one reusable decision-record template, one dedicated manifest, one dedicated Zig test, and one direct handoff checker; the packet also points at the directly coupled freeze-map, freeze-map-governance, review-checklist, parity-scorecard, indefinite-C policy, and shared Phase 15 build surfaces that must stay aligned with this lane's required review fields, decision buckets, reopen-trigger catalog, and no-approval posture without treating those support surfaces as review-process-owned maintenance lanes
- survey provenance refreshed against dated current-master readback marker `current-master-readback-2026-05-16` on 2026-05-16 after a fresh live reread confirmed the parked maintenance packet still carries the same no-approval posture, the same owner and required-approver evidence, and now a reusable decision-record template for future Architecture Council requests
- exact branch-head parity is not recorded for this parked review-process packet; the note uses an explicit dated readback marker instead of a quickly stale exact-head count while keeping the same bounded reviewer-facing maintenance follow-up
- maintenance handoff: this review-process slice is parked in maintenance mode until one of the named reopen triggers fires, the deep-core blocker posture changes, or the shared-summary companion lane in `Documentation/zigux/phase15-governance-lane-sequencing.md` reports drift that changes the truthfulness of this packet's required review fields, decision buckets, decision-record template, direct handoff checker, reopen-trigger catalog, or no-approval posture
- lane-owned packet:
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
  - `zigux/tests/phase15_architecture_council_review_process_manifest.json`
  - `zigux/tests/phase15_architecture_council_review_process.zig`
- directly coupled evidence surfaces:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `zigux/tests/phase15_build.zig`

## Why this slice exists

The roadmap's Phase 15 requirements include an Architecture Council review process, a parity scorecard, and the policy for code that remains in C indefinitely. Current `master` now carries the freeze map, stay-in-C governance language, and a landed parity-scorecard baseline, but this review-process note remains the reviewable record that says when the Architecture Council must be engaged, what evidence a request must carry, and what bounded outcomes are allowed.

That missing operational step left a governance gap between the roadmap and the live repo. A future patch could mention the Architecture Council in principle while still leaving reviewers to guess what artifact a status-change request must fill out and which decisions are legitimate inside the current mixed-language product plan.

The honest bounded follow-up is therefore still governance-only: keep the survey-grade review-process note, add one reusable decision-record template that turns the required packet fields into a concrete reviewer-facing artifact, and keep the direct handoff checker explicit so future maintenance rereads fail closed on the same bounded review-process packet instead of drifting back into generic shared-summary prose.

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
- the completed `Documentation/zigux/phase15-architecture-council-decision-record-template.md` artifact, or an exact equivalent record that preserves the same field order and labels
- the named owner for the lane, the required approver set, and the rollback owner
- the validation gate summary with links to the live evidence
- the evidence archive path that preserves linked surveys, blocker follow-ups, benchmark notes, and replay commands
- the latest blocker disposition saying whether the anchor remains blocked, is ready for narrower follow-up, or has been rejected for status change
- the automatic return-to-blocked trigger that says what stale summary, contradictory evidence, or route drift immediately returns the anchor to blocked posture instead of implying ongoing approval
- the current benchmark-notes status so reviewers can see whether performance evidence exists yet
- the replay command reviewers should run before trusting the current packet
- the rollback threshold that says what evidence loss, contradiction, or regression would force a retreat instead of a status change
- the retained discussion state that will be recorded if the review closes with a stay-in-C outcome
- the reopen triggers that cite one or more catalog items naming which evidence changes can reopen the discussion later without implying approval
- the trigger-specific evidence refresh that says what fresh linked evidence must be reread before a named reopen trigger can justify council attention again
- a parity scorecard link, or an explicit blocker record saying why the scorecard is not ready yet
- the indefinite-C policy link, or an explicit non-applicability note if the anchor is not governed by that policy surface
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
- new decision records should start from `Documentation/zigux/phase15-architecture-council-decision-record-template.md` so the same reviewer-facing field order survives from request to closeout
- the lane note must record the current status bucket, the chosen decision bucket, the decision record ID, the owner, the required approver set, the validation gate, the evidence archive path, the latest blocker disposition, the automatic return-to-blocked trigger, the current benchmark-notes status, the replay command, the rollback threshold, the retained discussion state, the reopen triggers, the trigger-specific evidence refresh, the parity scorecard link or blocker record, the indefinite-C policy link or non-applicability note, and the rollback owner
- if the council keeps the code in C, the blocker must remain explicit rather than disappearing into prose
- if the council keeps the code in C and closes active discussion, the retained discussion state must be `retired_from_active_discussion`, the automatic return-to-blocked trigger plus the trigger-specific evidence refresh must stay explicit, and the reopen triggers must stay attached to the evidence archive using one or more catalog items
- if the parity scorecard is missing, the record must say that clearly instead of implying silent approval

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for a retired stay-in-C packet is:

- `narrower_followup_answers_blocker`: a narrower seam inventory or follow-up now answers the latest blocker disposition without widening the approved boundary
- `evidence_packet_stale_or_contradictory`: linked validation, benchmark, survey, or blocker evidence has become stale or contradictory enough that the closed packet no longer stands on its own
- `ownership_or_validation_changed`: rollback ownership, lane ownership, or validation gates changed enough to invalidate the closed stay-in-C packet

Every retained stay-in-C closeout must cite at least one of these catalog items in its evidence archive so the scorecard, review-process note, and future exception records keep the same reopen vocabulary.

## Current Approval Posture

- no Architecture Council approval is currently recorded for a freeze-map status change
- the current bounded evidence is the freeze map, this review-process note, the reusable decision-record template, the dedicated review-process handoff checker, the review checklist hook, and `Documentation/zigux/phase15-parity-scorecard.md`
- current review-process evidence is limited to named `owner`, `required approver set`, `rollback owner`, evidence archive, blocker-disposition, automatic-return-to-blocked-trigger, benchmark-notes, replay-command, rollback-threshold, retained-discussion-state, reopen-trigger, trigger-specific-evidence-refresh, `parity scorecard link or blocker record`, and indefinite-C-policy records in the review packet plus the anchor-specific rollback-owner records in the parity scorecard
- until both the review record and the parity scorecard say otherwise, every freeze-in-C anchor remains blocked from an approval claim

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- Keep the Phase 15 governance lane in maintenance mode.
- replay before trusting this parked handoff:
  - `make -C zigux phase15-validate`
  - `make -C zigux phase15-test`
  - `zig build test --build-file zigux/tests/phase15_build.zig`
  - `make -C zigux phase15`
- reopen only when one of the named catalog triggers now fits the evidence packet, or when the deep-core blocker posture changes enough to justify a new bounded review-process follow-up
- next future target: stay in maintenance mode unless a named reopen trigger or the deep-core blocker posture changes; if a new same-lane review-process drift appears first, reread `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, and `zigux/tests/phase15_build.zig` together, then keep any repair scoped to the review-process packet instead of reopening shared-summary, parity-scorecard, or readiness packets

## Recorded Gaps

The current lane state is:

- landed `phase15-architecture-council-review-process-doc`
- landed `phase15-architecture-council-review-process-manifest`
- landed `phase15-architecture-council-review-process-test`
- landed `phase15-decision-record-template`
- landed `phase15-review-checklist-hook`
- landed `phase15-build-gate-review-process`
- landed `phase15-parity-scorecard-baseline`
- landed `phase15-evidence-archive-followup`
- landed `phase15-stay-in-c-retirement-rule`
- landed `phase15-reopen-trigger-catalog-followup`
- landed `phase15-review-packet-field-sync`
- landed `phase15-tests-readme-validator-route-sync`
- landed `phase15-docs-readme-maintenance-note-undercount`

The smaller machine-readable readiness exactness drift mentioned by older handoffs is already closed on current `master`: `zigux/tests/phase15_readiness_gate_manifest.json` and `scripts/zigux/validate-phase15.py` keep the dedicated docs-readme alignment guard explicit inside the shipped `phase15-validate` route.

This keeps the slice narrow. Zigux gains a reusable Architecture Council decision-record template beside the existing review-process note, keeps the landed freeze map, dedicated freeze-map governance packet, landed parity scorecard, indefinite-C policy, and dedicated review-process handoff checker linked through the same field vocabulary, preserves the retained stay-in-C closeout state and reopen-trigger catalog, states the current no-approval posture plainly, records the dated-readback provenance refresh that avoids a quickly stale exact-head count, and keeps future same-lane follow-up focused on review-process truthfulness rather than broader shared-summary drift.

## Non-goals

This slice does not claim:

- a full Architecture Council charter, roster, calendar, or voting system
- Architecture Council approval for any freeze-map status change
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- any new deep-core Zig bridge, wrapper, or direct port starter

## Gates

1. run the validator-first route
- `make -C zigux phase15-validate`

2. run the dedicated Phase 15 test target
- `make -C zigux phase15-test`

3. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

4. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Unless a named reopen trigger or the deep-core blocker posture changes first, keep this packet in maintenance mode. If a future follow-up is still inside the review-process lane, start with the template, the note, the dedicated handoff checker, and the manifest, and repair only the first field-order, decision-bucket, direct-guard, or no-approval posture drift that actually appears on current `master`.
