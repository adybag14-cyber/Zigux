# Phase 15 Architecture Council Review Process Survey

This document records the bounded Phase 15 governance lane around the Architecture Council review-process gap named in the roadmap.

## Status

- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_STATUS=review_process_slice_landed`
- `PHASE15_SLICE=architecture-council-review-process-governance-evidence-verification`
- scope: one review-process note, one dedicated manifest and Zig test, and one bounded governance, approval, and ownership evidence verification follow-up that keeps the explicit no-approval posture, anchor-template ownership packet, the scripts-root validator path, the dedicated handoff-checker route, the tests-root guidance path, and the last reviewed provenance aligned inside the same Architecture Council packet
- survey provenance last refreshed against reviewed `master` head `02264a3240cd30ce45c9a932047a0204b7ab5029`; later repo movement touching this review-process packet now requires a fresh bounded provenance refresh before this note should make a new current-`master` claim
- product boundary:
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/validate-phase15.py`
  - `zigux/tests/README.md`
  - `zigux/tests/phase15_architecture_council_review_process_manifest.json`
  - `zigux/tests/phase15_architecture_council_review_process.zig`
  - `zigux/tests/phase15_build.zig`

## Why this slice exists

The roadmap's Phase 15 requirements include an Architecture Council review process, a parity scorecard, and the policy for code that remains in C indefinitely. Current `master` already carries the freeze map, stay-in-C governance language, a landed parity-scorecard baseline, and this review-process note as the reviewable record that says when the Architecture Council must be engaged, what evidence a request must carry, and what bounded outcomes are allowed.

The current roadmap-versus-repo gap inside this slice is no longer a missing review-process artifact. The maintenance-mode task here is narrower: keep the trigger conditions, required packet fields, approval posture, reopen evidence rules, and shared handoff surfaces aligned with the same parked Phase 15 governance bundle instead of letting the process packet drift into stale or contradictory guidance.

That is the honest bounded role for this note now. It keeps the roadmap requirement concrete and reviewable without pretending the council already has a full roster, cadence, automation surface, or any approved freeze-map status change.

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
- the retained discussion state that will be recorded if the review closes with a stay-in-C outcome
- the automatic return-to-blocked trigger naming which missing field, stale evidence, contradictory scorecard link, or rollback-threshold breach forces the anchor back to blocked review posture
- the rollback threshold naming which decision-record, scorecard-evidence, benchmark-notes, replay-command, blocker-disposition, or rollback-owner drift forces the anchor back to blocked review posture
- the explicit `Documentation/zigux/phase15-indefinite-c-policy.md` link, or a note saying why the packet is not yet entering that policy posture
- the explicit note that the existing C implementation remains the product source of truth unless the Architecture Council approves the requested status change
- the reopen triggers that cite one or more catalog items naming which evidence changes can reopen the discussion later without implying approval
- the trigger-specific refreshed evidence by path for every named reopen trigger, together with the blocker disposition that reopened evidence is trying to change
- refreshed lane-owner and rollback-owner evidence whenever the reopen trigger is `ownership_or_validation_changed`
- a parity scorecard link, or an explicit blocker record saying why the scorecard is not ready yet
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
- the lane note must record the current status bucket, the chosen decision bucket, the decision record ID, the owner, the validation gate, the evidence archive path, the latest blocker disposition, the current benchmark-notes status, the replay command, the retained discussion state, the automatic return-to-blocked trigger, the rollback threshold, the indefinite-C policy link or applicability note, the reopen triggers, and the rollback owner
- if a packet reopens under `ownership_or_validation_changed`, active review cannot resume until the note refreshes both the current lane owner and the rollback owner in the reopened record
- if a packet reopens under any named trigger, the reopened note must cite the trigger-specific refreshed evidence by path and restate the current blocker disposition instead of naming the trigger alone
- if active status review begins, the packet must keep one automatic return-to-blocked trigger and the matching rollback threshold explicit so missing review fields, stale evidence, contradictory scorecard state, replay drift, blocker drift, or rollback-threshold breaches send the anchor back to blocked posture instead of relying on implied reviewer memory
- if active status review begins, the packet must also say plainly that the existing C implementation remains the product source of truth unless the Architecture Council approves the requested status change
- if the council keeps the code in C, the blocker must remain explicit rather than disappearing into prose
- if the council keeps the code in C, the review record must either link `Documentation/zigux/phase15-indefinite-c-policy.md` or say plainly why the packet is not yet using the indefinite-C policy surface
- if the council keeps the code in C and closes active discussion, the retained discussion state must be `retired_from_active_discussion` and the reopen triggers must stay attached to the evidence archive using one or more catalog items
- if the parity scorecard is missing, the record must say that clearly instead of implying silent approval

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for a retired stay-in-C packet is:

- `narrower_followup_answers_blocker`: a narrower seam inventory or follow-up now answers the latest blocker disposition without widening the approved boundary
- `evidence_packet_stale_or_contradictory`: linked validation, benchmark, survey, or blocker evidence has become stale or contradictory enough that the closed packet no longer stands on its own
- `ownership_or_validation_changed`: rollback ownership, lane ownership, or validation gates changed enough to invalidate the closed stay-in-C packet

Every retained stay-in-C closeout must cite at least one of these catalog items in its evidence archive so the scorecard, review-process note, and future exception records keep the same reopen vocabulary.

## Reopen Evidence Matrix

Every reopen request must do more than repeat a catalog trigger name. The packet must point reviewers at the trigger-specific refreshed evidence by path and restate the current blocker disposition that the reopened evidence is trying to change.

- `narrower_followup_answers_blocker`: cite the new narrower seam inventory, the updated validation plan, the rollback owner for that narrower seam, and the still-blocked boundary that remains in C unless the reopen request is approved
- `evidence_packet_stale_or_contradictory`: cite the exact linked evidence that went stale or contradictory, the refreshed blocker disposition, and the replacement validation or benchmark record that now reflects current repo truth
- `ownership_or_validation_changed`: cite the old and new owner or validation records, refresh the lane owner and rollback owner when ownership changed, and name the validation-gate or replay-command change that invalidated the closed packet

If multiple triggers are cited together, each trigger's minimum evidence must stay explicit in the same reopen packet instead of collapsing into one vague exception claim.

## Current Approval Posture

- no Architecture Council approval is currently recorded for a freeze-map status change
- the current bounded evidence is the freeze map, `Documentation/zigux/phase15-freeze-map-governance.md`, this review-process note, the review checklist hook, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and the reserved per-anchor templates under `Documentation/zigux/phase15-evidence-archives/`
- current approval evidence is explicit negative evidence rather than silence: this note records the no-approval posture, the parity scorecard still keeps every anchor in `freeze_in_c`, each reserved evidence-archive template keeps `requested decision bucket: pending_no_request`, `decision record ID: pending_no_architecture_council_request`, and `no Architecture Council approval claim` visible, and the review packet now keeps the automatic return-to-blocked trigger explicit if those fields or linked evidence drift
- current ownership evidence is explicit in both the scorecard and the anchor templates: `Documentation/zigux/phase15-parity-scorecard.md` names the lane owner, rollback owner, evidence archive path, latest blocker disposition, benchmark notes, replay command, and rollback threshold for each freeze-in-C anchor, and each matching evidence-archive template repeats those same owner and rollback-threshold records together with the validation gate summary, retained discussion state, automatic return-to-blocked trigger, indefinite-C policy link, and reopen triggers
- until the review record, `Documentation/zigux/phase15-freeze-map-governance.md`, the parity scorecard, the dedicated indefinite-C policy note, and the anchor templates all say otherwise, every freeze-in-C anchor remains blocked from an approval claim

## Roadmap Handoff Evidence

- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Phase 15, `Full-Parity Blockers and Long-Term Governance`
- roadmap handoff: the Architecture Council review process stays honest only while it remains visibly tied to the same Phase 15 governance bundle as the freeze map, parity scorecard, indefinite-C policy, shared replay gate, and parked maintenance-mode next step
- bootstrap ledger anchor: `docs(zigux): add documentation root, review checklist, and freeze map`
- current repo handoff: the original documentation-root and freeze-map landing is now carried forward by `Documentation/zigux/README.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, this review-process note, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/validate-phase15.py`, `zigux/tests/README.md`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15`
- current bounded lane: `P15-L08` keeps the review-process packet narrowed to one same-packet governance, approval, and ownership evidence verification refresh by replacing stale lane markers and directly coupled recorded-gap drift across the review-process note, manifest, and focused test so the Architecture Council handoff stays aligned with the current parked maintenance-mode Phase 15 packet, its scripts-root validator path, its dedicated handoff-checker route, its tests-root guidance path, and the neighboring governance slices as last reviewed at `master` head `02264a3240cd30ce45c9a932047a0204b7ab5029`; later repo movement now requires a fresh bounded provenance refresh before this note should restate that lane alignment for current `master`, without reopening freeze-map, parity-scorecard, or indefinite-C policy maintenance
- maintenance-mode next step: wait for one of the named reopen triggers, a shared Phase 15 replay drift, or the deep-core blocker posture to change before opening another Phase 15 slice

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `zig build test --build-file zigux/tests/phase15_build.zig`
  - `make -C zigux phase15`
- keep `scripts/zigux/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/validate-phase15.py`, and `zigux/tests/README.md` aligned with the same parked governance bundle so the scripts-root validator path, dedicated handoff-checker route, and tests-root guidance path do not drift away from the Architecture Council handoff while this lane remains parked
- reopen only when one of the named catalog triggers now fits the evidence packet, when the shared Phase 15 replay drifts, or when the deep-core blocker posture changes enough to justify a new bounded review-process follow-up
- next future target: wait for one of the named reopen triggers, a shared Phase 15 replay drift, or the deep-core blocker posture to change before opening another Phase 15 slice

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
- landed `phase15-ownership-refresh-gate`
- landed `phase15-review-checklist-roadmap-phase-rationale-sync`
- landed `phase15-automatic-return-to-blocked-gate`
- landed `phase15-indefinite-c-policy-review-gate`
- landed `phase15-review-process-roadmap-handoff-evidence`
- landed `phase15-review-process-reopen-evidence-matrix-gate`
- landed `phase15-review-process-rollback-threshold-field-gate`
- landed `phase15-review-process-source-of-truth-field-gate`
- landed `phase15-review-process-lane-identity-provenance-refresh`
- landed `phase15-review-process-indefinite-c-evidence-path-sync`
- landed `phase15-review-process-ownership-evidence-rollback-threshold-sync`
- landed `phase15-review-process-freeze-map-governance-handoff-sync`
- landed `phase15-review-process-scripts-tests-root-handoff-sync`

This keeps the slice narrow. Zigux gains a reviewable Architecture Council process description that now points at the landed parity scorecard, aligns the required packet with the scorecard's decision-record fields, keeps the dedicated freeze-map-governance companion explicit in the same parked handoff bundle, names the retained stay-in-C closeout state, standardizes the reopen-trigger catalog, requires refreshed ownership evidence when a packet reopens because ownership or validation changed, requires trigger-specific reopened evidence by path instead of trigger-name-only reopen requests, makes the automatic return-to-blocked trigger explicit in the review packet, promotes the rollback threshold from implied trigger wording to an explicit required request field, requires an explicit source-of-truth reminder inside the same request field set, keeps the current ownership-evidence inventory synced to the same rollback-threshold proof already required by the scorecard and the reserved anchor templates, keeps the current roadmap phase and written rationale explicit in the shared checklist, keeps the roadmap and ledger provenance explicit in the same handoff surface, refreshes the packet's own lane-identity and provenance markers so the note, manifest, and focused test stay aligned with the current parked maintenance-mode Phase 15 packet and the neighboring Phase 15 governance packet family, keeps the scripts-root validator path, dedicated handoff-checker route, and tests-root guidance path visible inside the same handoff packet, and states the current no-approval posture plainly, but it still does not claim a real council roster or any change to a freeze-map anchor status.

## Non-goals

This slice does not claim:

- a full Architecture Council charter, roster, calendar, or voting system
- Architecture Council approval for any freeze-map status change
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- any new deep-core Zig bridge, wrapper, or direct port starter

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The checklist field-sync and automatic return-to-blocked follow-ups are now landed, so the next honest action is to wait for one of the named reopen triggers, a shared Phase 15 replay drift, or the deep-core blocker posture to change before opening another Phase 15 slice.
