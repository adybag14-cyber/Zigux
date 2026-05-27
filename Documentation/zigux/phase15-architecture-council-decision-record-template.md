# Phase 15 Architecture Council Decision Record Template

Use this template when a freeze-map anchor enters Architecture Council status review.

This is a review packet template, not approval by itself.

## Record Metadata

- `DECISION_RECORD_ID=<replace-with-stable-id>`
- decision record ID:
- `PHASE=Phase 15`
- `LANE_KEY=<replace-with-lane-key>`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`

## Anchor And Ownership

- exact Linux anchor path:
- roadmap phase:
- lane owner:
- current status bucket:
- requested decision bucket:
- required approver set:
- rollback owner:

## Validation And Evidence

- validation gate summary:
- evidence archive path:
- latest blocker disposition:
- benchmark notes:
- replay command:
- rollback threshold:

## Stay-In-C Closeout

- the retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- governance lane sequencing link or explicit scope note:
- `retired_from_active_discussion` state:
- automatic return-to-blocked trigger:
- the reopen triggers:
- the trigger-specific evidence refresh:
- the evidence archive path that will be refreshed before any later reopen request:

## Reopen Evidence

- the exact reopen trigger being exercised:
- refreshed evidence by path:
- the blocker disposition being challenged:
- the narrower seam or policy change that makes the new review safe to consider:

## Supporting Context

- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

## Review Outcome

- closeout result:
- follow-up owner:
- next bounded step:

## Usage Rules

- Prefer the dated master readback form for parked governance and stay-in-C review packets.
- Only record an exact head when the linked review needs it to anchor a named published decision, and explain that exception in the exact-head provenance exception note.
- Any exact-head provenance exception must keep the lane owner, rollback owner, and required approver set explicit and explain why dated master readback is insufficient for the named published decision.
- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
- A stay-in-C closeout must keep the retained `freeze_in_c` decision, the current blocker, the required approver set, the governance lane sequencing link or explicit scope note, the automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, and the evidence archive path that will be refreshed before any later reopen request explicit.
- A reopen request must cite the exact reopen trigger being exercised, refreshed evidence by path, the blocker disposition being challenged, and the narrower seam or policy change that makes the new review safe to consider.