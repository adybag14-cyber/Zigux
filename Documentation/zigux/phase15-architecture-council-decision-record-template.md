# Phase 15 Architecture Council Decision Record Template

Use this template when a freeze-map anchor enters Architecture Council status review. It keeps the review-process note, freeze-map governance packet, parity scorecard, and indefinite-C policy talking about the same required fields in the same order.

## Template Status

- `PHASE15_TEMPLATE_STATUS=review_packet_template_ready`
- `PHASE15_TEMPLATE_SCOPE=freeze_map_status_review`
- `PHASE15_TEMPLATE_BOUNDARY=reviewable_artifact_only`
- no field in this template implies approval until the completed record is linked from the requesting lane, the evidence archive, and the parity scorecard row for the same anchor

## Required Header Fields

- `DECISION_RECORD_ID=replace-with-stable-id`
- `LINUX_ANCHOR_PATH=replace-with-linux-path`
- `CURRENT_ROADMAP_PHASE=Phase 15`
- `CURRENT_STATUS_BUCKET=freeze_in_c|study_only`
- `REQUESTED_DECISION_BUCKET=keep_in_c|study_only_followup|bounded_dual_implementation|defer_or_reject`
- `LANE_OWNER=replace-with-owner`
- `REQUIRED_APPROVER_SET=replace-with-approver-set`
- `ROLLBACK_OWNER=replace-with-rollback-owner`

## Evidence Fields

- `VALIDATION_GATE_SUMMARY=replace-with-summary-and-links`
- `EVIDENCE_ARCHIVE_PATH=replace-with-phase15-evidence-archive-path`
- `LATEST_BLOCKER_DISPOSITION=replace-with-current-blocker-state`
- `AUTOMATIC_RETURN_TO_BLOCKED_TRIGGER=replace-with-fail-closed-trigger`
- `BENCHMARK_NOTES_STATUS=replace-with-benchmark-state-or-pending-marker`
- `REPLAY_COMMAND=replace-with-current-replay-command`
- `ROLLBACK_THRESHOLD=replace-with-threshold`
- `PARITY_SCORECARD_LINK_OR_BLOCKER_RECORD=replace-with-path-or-explicit-blocker`
- `INDEFINITE_C_POLICY_LINK_OR_NON_APPLICABILITY_NOTE=replace-with-path-or-note`

## Decision Closeout Fields

- `RETAINED_DISCUSSION_STATE=active_discussion|retired_from_active_discussion`
- `REOPEN_TRIGGERS=replace-with-one-or-more-catalog-items`
- `TRIGGER_SPECIFIC_EVIDENCE_REFRESH=replace-with-required-reread-set`
- `EXPLICIT_NON_GOALS=replace-with-bounded-non-goals`
- `WRITTEN_RATIONALE=replace-with-rationale`
- `DECISION_SUMMARY=replace-with-final-outcome-summary`

## Fill-In Rules

- Keep the exact Linux anchor path, current status bucket, and requested decision bucket explicit.
- Reuse the reopen-trigger catalog from `Documentation/zigux/phase15-architecture-council-review-process.md` instead of inventing new reopen vocabulary.
- If the outcome is `keep_in_c`, keep the blocker explicit and set `RETAINED_DISCUSSION_STATE=retired_from_active_discussion` only when the evidence archive still carries the reopen triggers and trigger-specific evidence refresh.
- If the parity scorecard is not ready, keep the blocker record explicit instead of leaving the field blank.
- If the indefinite-C policy does not apply, state why instead of omitting that field.
- Keep the artifact narrow: this template records one bounded freeze-map decision request and does not widen into a subsystem plan, charter, roster, or implementation backlog.

## Minimal Review Flow

1. Copy this template into the requesting lane's evidence archive.
2. Fill every required field before asking for Architecture Council attention.
3. Link the completed record from the freeze-map-adjacent lane note and the matching parity-scorecard row.
4. Re-run the current Phase 15 validation and replay routes before treating the record as reviewable.

## Non-goals

This template does not claim:

- Architecture Council approval by itself
- a new deep-core implementation lane
- a substitute for the freeze map, parity scorecard, or indefinite-C policy
- a permanent council charter, voting system, or meeting cadence
