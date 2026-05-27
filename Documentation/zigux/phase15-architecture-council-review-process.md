# Phase 15 Architecture Council Review Process

This note records the bounded Phase 15 review-policy packet for freeze-map anchors that remain in C indefinitely.

## Status

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_SLICE=stay-in-c-review-field-inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`
- `PHASE15_PACKET_OWNER=Architecture Council`
- `PHASE15_PACKET_VALIDATION_GATE=python3 scripts/zigux/check-phase15-review-process-handoff.py && zig test zigux/tests/phase15_architecture_council_review_process.zig && zig build test --build-file zigux/tests/phase15_architecture_council_review_process_build.zig`
- `PHASE15_PACKET_ROLLBACK_OWNER=Architecture Council`
- no Architecture Council approval is currently recorded for a freeze-map status change
- this note keeps the roadmap-required Architecture Council review-process surface honest on current `master`: the docs-root field inventory, the dedicated decision-record template, the dedicated review-process manifest, the focused review-process handoff checker, the focused tests-root alignment guard, the focused Zig replay, and the focused build-file replay are landed, while the broader validator-first shared-summary surfaces remain gap-tracked by `Documentation/zigux/phase15-shared-summary-gap.md`

## Purpose

The Phase 15 roadmap keeps deep-core status changes under human governance, not implementation momentum.

That means any request to move a freeze-in-C anchor out of its current blocked posture must arrive as an explicit Architecture Council review packet with named owners, named evidence, and an honest stay-in-C fallback when the evidence is incomplete.

This note exists to keep that review-policy surface explicit beside `Documentation/zigux/phase15-architecture-council-decision-index.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`.

## Required review packet

Any freeze-map anchor entering Architecture Council status review must keep all of the following explicit:

- exact Linux anchor path
- roadmap phase
- decision record ID
- lane owner
- current status bucket
- requested decision bucket
- required approver set
- rollback owner
- validation gate summary
- evidence archive path
- latest blocker disposition
- benchmark notes
- replay command
- rollback threshold
- automatic return-to-blocked trigger
- `retired_from_active_discussion` state
- reopen triggers
- trigger-specific evidence refresh
- parity scorecard link or blocker record
- indefinite-C policy link or explicit non-applicability note
- governance lane sequencing link or explicit scope note
- study-only anchor accounting link or explicit freeze-map-anchor confirmation
- explicit non-goals
- written rationale

If one of those fields cannot be stated honestly, the request stays blocked and the C implementation remains the product source of truth.

## Study-only boundary

Study-only freeze-map anchors stay outside this Architecture Council status-review packet until the freeze map itself changes.

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`, not candidates for a freeze-in-C status review through this note, unless the freeze map and supporting governance packet are explicitly updated first.

## Review outcomes

The Architecture Council may close a request only in one of these bounded ways:

- keep the anchor in `freeze_in_c`
- reopen review later with narrower evidence
- approve a status-bucket change in a separately linked decision record

Every closeout record must also keep all of the following explicit in the linked decision record:

- closeout result
- follow-up owner
- next bounded step

If those outcome fields cannot be named honestly, the request stays blocked instead of presenting a stay-in-C closeout or status-bucket change as more settled than the current evidence supports.

This note does not define an exception path outside those reviewable outcomes.

## Stay-in-C closeout rule

If a freeze-in-C review closes without a status change, the closeout record must keep all of the following explicit:

- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- the governance lane sequencing link or explicit scope note
- `retired_from_active_discussion` state
- the automatic return-to-blocked trigger
- the reopen triggers
- the trigger-specific evidence refresh
- the evidence archive path that will be refreshed before any later reopen request

A closed stay-in-C record is not approval debt. It is an explicit decision to keep the anchor in C until narrower evidence exists.

## Reopen evidence rule

A later reopen request must not rely on generic intent alone. It must cite:

- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider

If the refreshed evidence is missing, contradictory, or broader than the allowed seam, the request returns to blocked review posture immediately.

## Current Phase 15 posture

On current `master`, no freeze-map anchor has an Architecture Council approval for a status change.

The current honest packet is therefore docs-root governance plus gap tracking:

- `Documentation/zigux/phase15-freeze-map-governance.md` keeps the freeze anchor inventory, blocker posture, required approver sets, rollback owners, and evidence-archive paths explicit
- `Documentation/zigux/phase15-parity-scorecard.md` keeps the blocked-posture accounting explicit
- `Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py` keeps the shared review-checklist summary for `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` aligned with `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, and this note without implying that the study-only anchors have entered freeze-in-C status review
- `scripts/zigux/check-phase15-tests-readme-alignment.py` is the focused guard for the landed tests-root Phase 15 governance reminder in `zigux/tests/README.md`; keep that tests-root surface aligned with `Documentation/zigux/phase15-shared-summary-gap.md` and this owner note while the broader validator-first and build-route companions remain gap-tracked
- `Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md` keeps the review record shape explicit for future Architecture Council requests, defaults that record to dated-master-readback provenance, and requires an explicit exception note before exact-head provenance is used
- `Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current Architecture Council decision inventory explicit, recording that no freeze-map anchor has an approved status change or stay-in-C closeout record on current `master` until a future decision record lands
- `zigux/tests/phase15_architecture_council_review_process_manifest.json` keeps the dedicated review-packet field inventory machine-readable
- `scripts/zigux/check-phase15-review-process-handoff.py` keeps the review-process packet, the maintenance handoff, and the shared-summary-gap dependency aligned
- `zigux/tests/phase15_architecture_council_review_process.zig` keeps the focused review-process replay explicit beside the docs and manifest-backed packet
- `zigux/tests/phase15_architecture_council_review_process_build.zig` keeps a focused `zig build test --build-file zigux/tests/phase15_architecture_council_review_process_build.zig` replay available for this packet without implying that the broader Phase 15 make routes or validator-first routes are landed
- `Documentation/zigux/phase15-shared-summary-gap.md` keeps the broader validator-first shared-summary surfaces explicit instead of letting this note imply that they have already landed
- this note keeps the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule explicit

Together, those surfaces define the review policy without claiming that any deep-core anchor is ready to leave C.

## Maintenance-mode handoff

This packet should stay narrow.

If a future lane reopens it, prefer one of these equally bounded follow-ups:

- keep the shared entry-review prompt in `Documentation/zigux/review-checklist.md` pointed at this note without treating the broad checklist as the owner of the exact Architecture Council field inventory
- keep the shared study-only anchor summary in `Documentation/zigux/review-checklist.md` aligned with `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `Documentation/zigux/freeze-map.md`, and `Documentation/zigux/phase15-study-only-anchor-accounting.md` before widening into broader Phase 15 prose
- keep the landed shared tests-root Phase 15 governance reminder in `zigux/tests/README.md` aligned with `scripts/zigux/check-phase15-tests-readme-alignment.py`, this note, and `Documentation/zigux/phase15-shared-summary-gap.md` before widening into broader Phase 15 prose
- keep `Documentation/zigux/phase15-architecture-council-decision-record-template.md` aligned with this note before widening into broader Phase 15 prose
- keep `Documentation/zigux/phase15-architecture-council-decision-index.md` aligned with this note and the decision-record template before widening into broader Phase 15 prose
- keep the dedicated review-process manifest, the focused Zig replay, the focused build-file replay, and the focused handoff checker aligned with this note before widening into broader Phase 15 prose
- keep the restored dedicated indefinite-C policy companion aligned without widening into unrelated Phase 15 prose
- if the broader validator-first packet truly lands later, align this note with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, and `zigux/tests/phase15_architecture_council_review_process_manifest.json` before claiming those broader surfaces as current evidence here

Until then, treat this note as the Architecture Council source of truth for review-packet shape and stay-in-C closeout behavior.

## Non-goals

This note does not claim:

- an Architecture Council approval for any freeze-map status change
- a broader validator-first route as current landed evidence here
- a deep-core Zig bridge, wrapper, or status change

## Next bounded step

Keep this lane parked unless fresh repo inspection shows a new same-packet field drift in the Architecture Council request inventory, the stay-in-C closeout rule, the reopen-evidence rule, the decision index, the focused review-process replay, the focused build-file replay, the landed tests-root Phase 15 governance reminder, or the current shared-summary gap tracking for the broader validator-first surfaces.