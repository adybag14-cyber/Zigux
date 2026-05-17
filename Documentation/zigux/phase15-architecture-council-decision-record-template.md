# Phase 15 Architecture Council Decision Record Template

Use this template when a freeze-map anchor enters Architecture Council status review.

This is a review packet template, not approval by itself.

## Record Metadata

- `DECISION_RECORD_ID=<replace-with-stable-id>`
- decision record ID:
- `PHASE=Phase 15`
- `LANE_KEY=P15-L08`
- `SURVEYED_COMMIT=<replace-with-dated-master-readback-or-exact-head>`
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

- retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- `retired_from_active_discussion` state:
- automatic return-to-blocked trigger:
- reopen triggers:
- trigger-specific evidence refresh:
- the evidence archive path that will be refreshed before any later reopen request:

## Supporting Context

- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

## Review Outcome

- closeout result:
- follow-up owner:
- next bounded step:

## Usage Rules

- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
- A stay-in-C closeout must keep the retained `freeze_in_c` decision, the current blocker, the required approver set, the automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, and the evidence archive path that will be refreshed before any later reopen request explicit.
- A reopen request must cite the exact reopen trigger being exercised, refreshed evidence by path, the blocker disposition being challenged, and the narrower seam or policy change that makes the review safe to consider.
