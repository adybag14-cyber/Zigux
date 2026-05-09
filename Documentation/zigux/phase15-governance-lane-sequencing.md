# Phase 15 Governance Lane Sequencing

This note turns the current Phase 15 governance evidence into one bounded anti-overlap map for scheduled governance lanes.

It is a coordination artifact, not an approval record and not a freeze-map status change.

## Current posture

- `PHASE15_STATUS=parked_governance_packet`
- `PHASE15_SEQUENCE=governance-lane-anti-overlap`
- shared validator-first routes already present on `master`: `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`, `python3 scripts/zigux/check-phase15-review-process-handoff.py`, and `make -C zigux phase15-validate`
- shared replay routes already present on `master`: `make -C zigux phase15-test`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15`

## Why this note exists

The current Phase 15 packet is already real product progress:

- the readiness gate records the live governance bundle and the remaining deep-core blocker posture
- the freeze-map governance packet records the current no-approval posture for freeze-map anchors
- the Architecture Council review-process packet records the required review fields and bounded decision buckets
- the parity scorecard records per-anchor blocker dispositions and evidence-archive destinations
- the handoff packet records the parked next-step posture
- the indefinite-C packet records the long-term stay-in-C rules, blocker-evidence replay, and lane-owner vocabulary

Without a dedicated sequencing note, nearby scheduled governance runs can still reopen the same packet from different directions just because the files live close together.

## Lane map

### 1. Readiness lane: packet status only

Use the readiness lane when the work is about whether the current Phase 15 governance packet is still parked, still green, and still blocked only on the same deep-core status-change evidence.

Own:

- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `zigux/tests/phase15_readiness_gate.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`

Do not use this lane to rewrite the parity scorecard, freeze-map governance packet, or Architecture Council review-process fields unless the readiness packet can no longer summarize them truthfully.

### 2. Freeze-map governance lane: `P15-L04` freeze-anchor posture only

Use the freeze-map governance lane `P15-L04` when the work is about the freeze set, the explicit no-approval posture, or linked blocker evidence for the frozen anchors.

Own:

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `zigux/tests/phase15_freeze_map_governance.zig`

Do not use this lane to edit the Architecture Council review-process packet, the handoff packet, or the shared build summary unless the freeze-map packet itself is no longer reviewable.

### 3. Review-process lane: Architecture Council packet only

Use the review-process lane when the work is about required review fields, bounded decision buckets, rollback-threshold wording, or the dedicated handoff checker for that packet.

Own:

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`

Do not use this lane to change any deep-core blocker disposition or parity-scorecard owner record unless the review-process packet can no longer describe the existing scorecard honestly.

### 4. Parity-scorecard lane: per-anchor blocker records only

Use the parity-scorecard lane when the work is about per-anchor owners, evidence-archive destinations, blocker dispositions, benchmark-note status, or retained stay-in-C closeout state.

Own:

- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-evidence-archives/`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_parity_scorecard.json`

Do not use this lane to edit the handoff packet or shared docs summaries unless the scorecard can no longer be summarized truthfully from those surfaces.

### 5. Handoff lane: `P15-L08` parked next-step record only

Use the handoff lane `P15-L08` when the work is about the dedicated next-step packet, its manifest, or the statement that the current governance bundle should remain parked until a named reopen trigger fires or the blocker posture changes.

Own:

- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`

Do not use this lane to move a freeze-map anchor, rewrite a scorecard blocker, or broaden the Architecture Council process.

### 6. Indefinite-C policy lane: stay-in-C policy and blocker-evidence wording only

Use the indefinite-C policy lane when the work is about the long-term policy for code that remains in C indefinitely, the documented exception posture, the blocker-evidence replay, or the lane-owner vocabulary alignment tied to that packet.

Own:

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

Do not use this lane to restate readiness, handoff, or scorecard status unless the policy packet itself has drifted.

### 7. Shared summary and build-wiring lane: `P15-L06`

Use this sequencing lane only when the owner split itself has drifted across shared surfaces.

Own:

- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- the shared build-wire touch in `zigux/tests/phase15_build.zig`

When this lane touches a shared summary surface, keep that summary compact and boundary-first.
A shared summary such as `Documentation/zigux/review-checklist.md` does not need to re-enumerate every Phase 15 owner-map, readiness, handoff-manifest, or blocker-evidence replay if those details remain explicit in this sequencing note, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, and `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`.

This lane may also touch one shared summary surface such as `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `Documentation/zigux/review-checklist.md`, but only when that summary is blurring the current owner split.

Do not use this lane to change any deep-core blocker disposition, any Architecture Council approval posture, or any packet-local evidence field that belongs to one of the owning lanes above.

## Current anti-overlap correction

The strongest current Phase 15 sequencing rule is simple:

- keep packet-local truthfulness or evidence changes inside the owning lane above
- keep shared summaries compact while packet-local replay inventories stay in the sequencing note, readiness note, handoff note, or dedicated replay guards
- use `P15-L06` only for shared summaries or shared build wiring
- keep every Phase 15 governance run parked unless a named reopen trigger fires or the deep-core blocker posture changes
- current `master` already closed the older shared tests-root follow-through around `zigux/tests/phase15_indefinite_c_blocker_evidence.zig` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so future `P15-L06` runs should not reopen that earlier tests-root touch unless one of those anchors disappears again
- current `master` still carries one narrower shared-summary follow-through: `zigux/tests/README.md` keeps the dedicated `make -C zigux phase15-test` route explicit, but it still leaves `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_readiness_gate_manifest.json` implicit there, and `scripts/zigux/check-phase15-scripts-readme-alignment.py` still does not fail-close on those two omissions, so the next honest `P15-L06` shared touch stays bounded to that exact tests-root plus checker manifest-pair sync rather than reopening broader summaries
- current `master` also already closed the earlier docs-root workflow follow-through: `Documentation/zigux/README.md` explicitly carries `.github/workflows/zigux-bootstrap.yml` beside the checker-backed and build-backed replay routes, so future `P15-L06` runs should not reopen that docs-root touch unless the workflow pointer or the shared owner split drifts again
- current `master` also already closed the earlier review-checklist workflow-and-build follow-through: `Documentation/zigux/review-checklist.md` explicitly carries `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15-validate`, so future `P15-L06` runs should not reopen that checklist touch unless one of those shared governance anchors drifts again
- current `master` now keeps the current handoff provenance wording isolated inside the owning handoff packet: `Documentation/zigux/phase15-handoff-next-steps-survey.md` and `zigux/tests/phase15_handoff_next_steps_manifest.json` both carry `dated_master_readback_same_marker_alignment`, and the paired `Documentation/zigux/phase15-parity-scorecard.md` packet carries the same dated `current-master-readback-2026-05-09` marker, so future provenance refreshes stay handoff-lane `P15-L08` work unless that packet-alignment wording also blurs a shared summary surface
- if current `master` moves ahead of a packet's reviewed-head marker while the blocker posture and owner split stay parked, treat that provenance refresh as handoff-lane `P15-L08` work first; do not reopen `P15-L06` unless the stale reviewed-head wording also blurs a shared summary surface

## Recommended next-step order

1. shared summary and build-wiring lane first only for the still-open tests-root plus checker manifest-pair undercount: `zigux/tests/README.md` and `scripts/zigux/check-phase15-scripts-readme-alignment.py` still need to keep `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_readiness_gate_manifest.json` explicit beside the already-named dedicated `make -C zigux phase15-test` route, and any `P15-L06` touch should stay bounded to that exact repair unless another shared-summary drift appears
2. the owning packet lane when one note, manifest, checker, or replay route stops matching current `master`
3. no deep-core status-change work until the blocker posture changes enough to justify a fresh Architecture Council slice

## Anti-overlap rule

If a scheduled Phase 15 run is assigned one owning lane, keep the work inside that packet plus the smallest unavoidable shared touch.

If `P15-L06` is assigned, do not consume packet-local backlog just because the shared sequencing lane has spare room.
