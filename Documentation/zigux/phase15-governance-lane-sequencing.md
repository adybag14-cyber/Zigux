# Phase 15 Governance Lane Sequencing

This note records the bounded Phase 15 Architecture Council sequencing packet for the parked governance lanes that keep freeze-map decisions, review boundaries, and stay-in-C policy truthful.

## Status

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_SLICE=architecture-council-governance-lane-boundaries`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`
- current repo reality: the core Phase 15 governance notes are landed, the dedicated review-process manifest is landed, the dedicated governance-lane sequencing manifest plus focused replay are landed, the focused parity-scorecard machine-readable companion plus focused replay are landed, the dedicated Architecture Council packet checker `scripts/zigux/check-phase15-architecture-council-packet.py` is landed, the dedicated handoff manifest plus focused handoff-specific replay plus focused handoff-note checker are landed, the focused indefinite-C lane-owner companion `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` is landed, the focused review-checklist study-only alignment checker is landed, the dedicated validator-first companion `scripts/zigux/validate-phase15.py` is directly materialized, the dedicated shared build companion `zigux/tests/phase15_build.zig` is now directly materialized, the dedicated deep-core blocker survey is now landed, and the remaining broader repo-reality gaps stay narrowed to missing Phase 15 make-wrapper and shared-CI route bodies rather than a missing build companion
- scope: keep one reviewable record of which Phase 15 governance lane owns which reminder surface, which shared checks may speak for the parked governance packet, and which adjacent route-level gaps must stay explicit instead of being silently treated as landed

## Purpose

Phase 15 is a governance tranche, not a hidden deep-core delivery lane.

That means the repo needs one compact sequencing note that says:

- which Architecture Council packet owns freeze-map status review
- which neighboring packet owns blocked-posture accounting
- which neighboring packet owns the stay-in-C policy vocabulary
- which neighboring packet owns the dedicated roadmap-versus-repo blocker crosswalk for the deep-core freeze-in-C anchors
- which neighboring packet owns the study-only anchor inventory outside blocked status-change rows
- which reminder surfaces may describe those packets together
- which remaining missing wrapper-route and shared-CI companions must remain named as gaps instead of being implied as shipped evidence

This note exists so the docs-root, checklist-specific, and scripts-side alignment checks can name a real sequencing companion instead of pointing at a stale governance snapshot.

## Lane inventory

The current bounded Phase 15 governance packet is split this way:

- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set, required approver sets, rollback owners, evidence archive paths, and blocker posture for the deep-core freeze-in-C anchors
- `Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk for the four freeze-in-C anchors and keeps the blocker survey reviewable without widening the freeze-map owner packet into a broader shared-summary reminder
- `Documentation/zigux/phase15-parity-scorecard.md`, `zigux/tests/phase15_parity_scorecard.json`, and `zigux/tests/phase15_parity_scorecard.zig` own blocked-posture accounting and the machine-readable parity-scorecard companion that keeps the current freeze-map posture explicit beside the human-readable scorecard
- `Documentation/zigux/phase15-architecture-council-review-process.md` owns the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule
- `scripts/zigux/check-phase15-architecture-council-packet.py` keeps the dedicated Architecture Council request packet aligned with the sequencing note and neighboring reminder surfaces without turning shared reminder docs into owners of the request packet
- `Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary for anchors that remain in C indefinitely
- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows
- `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces that may summarize or rerun the packet, but they do not own freeze-map status decisions
- `Documentation/zigux/phase15-shared-summary-gap.md` owns the broad reminder-surface drift tracking that keeps shared docs, scripts, and tests wording honest without treating blocked Phase 15 make-wrapper or shared-CI routes as shipped evidence
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py` keeps the checklist-specific study-only anchor summary boundary aligned with `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` without widening the checklist into an owner of freeze-map status decisions
- `scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate for the bounded governance packet without widening the lane into a make-wrapper or shared-route claim
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit without widening into a broader wrapper-route claim
- `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `scripts/zigux/check-phase15-handoff-note-alignment.py` keep the handoff-specific inventory, focused handoff-specific replay, and focused handoff-note alignment explicit without turning the sequencing packet into the owner of the handoff packet itself

## Sequencing rules

Keep the Phase 15 governance lanes sequenced in this order when fresh review work appears:

1. refresh repo reality for the freeze-map anchor set and blocker posture first
2. refresh the dedicated deep-core blocker survey if the roadmap-versus-current-master crosswalk changes
3. refresh the parity scorecard only if a blocker posture, owner, approver set, or evidence path changed
4. refresh the Architecture Council review-process packet only if the request-field inventory, stay-in-C closeout rule, or reopen-evidence rule changed
5. refresh the indefinite-C policy packet only if the stay-in-C vocabulary or reopen-trigger catalog changed
6. refresh readiness, handoff, shared-build, study-only-accounting, shared-summary, and other reminder surfaces only after the owning packet already says the same thing

This ordering keeps the Architecture Council source-of-truth files ahead of broad reminder prose.

## Shared-surface boundaries

The shared reminder surfaces may say that:

- no Architecture Council approval is currently recorded for a freeze-map status change
- the current deep-core posture is blocked and maintenance-only
- the validator-first replay and the dedicated shared-build replay are directly readable, while the broader Phase 15 make-wrapper and shared-CI routes still remain gap-tracked

The shared reminder surfaces must not say that:

- a deep-core status change has been approved
- a freeze-in-C anchor is ready for a direct Zigux bridge
- a missing focused replay, blocked make-wrapper route, or absent shared-CI companion is already landed on current `master`

## Current repo-reality gaps

Current `master` still lacks the broader Phase 15 route companions that reminder surfaces may still mention:

- no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`
- `.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`

Those route gaps do not erase the landed governance packet or the directly readable `zigux/tests/phase15_build.zig` shared build companion.

They do mean any shared reminder surface must keep those wrapper-route and shared-CI surfaces framed as blocked current-master gaps rather than silently treating them as direct evidence.

## Maintenance-mode handoff

- current lane posture: `maintenance_mode`
- replay only when one of these packet-local conditions becomes true:
  - `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
  - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-tests-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-architecture-council-packet.py`
  - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
  - `python3 scripts/zigux/check-phase15-handoff-note-alignment.py`
  - `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
  - `python3 scripts/zigux/validate-phase15.py`
  - `zig build test --build-file zigux/tests/phase15_build.zig`
  - `zig test zigux/tests/phase15_governance_lane_sequencing.zig`
- reopen only when one of these packet-local conditions becomes true:
  - a Phase 15 owner packet changes its lane boundary or reminder ownership
  - the directly readable `zigux/tests/phase15_build.zig` shared build companion disappears or its packet boundary changes
  - a broader Phase 15 make-wrapper or shared-CI route lands on current `master`
  - a shared reminder surface starts claiming Phase 15 approval or current evidence that the owning packet does not support
- if this lane reopens, reread `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-deep-core-blocker-survey.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_build.zig`, `scripts/zigux/check-phase15-architecture-council-packet.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, and `scripts/zigux/validate-phase15.py` together before widening any shared reminder text

## Non-goals

This note does not claim:

- an Architecture Council approval for any freeze-map status change
- a new deep-core Zig bridge, wrapper, or dual implementation
- that the blocked broader Phase 15 make-wrapper or shared-CI route surfaces are already present on current `master`

## Next bounded step

Keep this lane parked until one of the owner packets changes enough that the shared reminder boundaries need another truthfulness refresh, the directly readable `zigux/tests/phase15_build.zig` companion changes enough to force a packet rewrite, or one of the broader Phase 15 make-wrapper or shared-CI route surfaces finally lands and needs to be folded into the sequencing story.