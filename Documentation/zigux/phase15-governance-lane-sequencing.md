# Phase 15 Governance Lane Sequencing

This note turns the current Phase 15 governance evidence into one bounded anti-overlap map for scheduled governance lanes.

It is a coordination artifact, not an approval record and not a freeze-map status change.

## Current posture

- `PHASE15_STATUS=parked_governance_packet`
- `PHASE15_SEQUENCE=governance-lane-anti-overlap`
- shared validator-first routes already present on `master`: `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`, `python3 scripts/zigux/check-phase15-review-process-handoff.py`, and `make -C zigux phase15-validate`
- shared replay routes already present on `master`: `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15`

## Why this note exists

The current Phase 15 packet is already real product progress:

- the readiness gate records the live governance bundle and the remaining deep-core blocker posture
- the freeze-map governance packet records the current no-approval posture for freeze-map anchors
- the Architecture Council review-process packet records the required review fields and bounded decision buckets
- the parity scorecard records per-anchor blocker dispositions and evidence-archive destinations
- the handoff packet records the parked next-step posture
- the indefinite-C packet records the long-term stay-in-C rules and lane-owner vocabulary

Without a dedicated sequencing note, nearby scheduled governance runs can still reopen the same packet from different directions just because the files live close together.

## Lane map

### 1. Readiness lane: packet status only

Use the readiness lane when the work is about whether the current Phase 15 governance packet is still parked, still green, and still blocked only on the same deep-core status-change evidence.

Own:

- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `zigux/tests/phase15_readiness_gate.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`

Do not use this lane to rewrite the parity scorecard, freeze-map governance packet, or Architecture Council review-process fields unless the readiness packet can no longer summarize them truthfully.

### 2. Freeze-map governance lane: freeze-anchor posture only

Use the freeze-map governance lane when the work is about the freeze set, the explicit no-approval posture, or linked blocker evidence for the frozen anchors.

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

### 5. Handoff lane: parked next-step record only

Use the handoff lane when the work is about the dedicated next-step packet, its manifest, or the statement that the current governance bundle should remain parked until a named reopen trigger fires or the blocker posture changes.

Own:

- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`

Do not use this lane to move a freeze-map anchor, rewrite a scorecard blocker, or broaden the Architecture Council process.

### 6. Indefinite-C policy lane: stay-in-C policy wording only

Use the indefinite-C policy lane when the work is about the long-term policy for code that remains in C indefinitely or the lane-owner vocabulary alignment tied to that packet.

Own:

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

Do not use this lane to restate readiness, handoff, or scorecard status unless the policy packet itself has drifted.

### 7. Shared summary and build-wiring lane: `P15-Y06`

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
- use `P15-Y06` only for shared summaries or shared build wiring
- keep every Phase 15 governance run parked unless a named reopen trigger fires or the deep-core blocker posture changes

## Recommended next-step order

1. shared summary and build-wiring lane only when the owner split itself drifts
2. the owning packet lane when one note, manifest, checker, or replay route stops matching current `master`
3. no deep-core status-change work until the blocker posture changes enough to justify a fresh Architecture Council slice

## Anti-overlap rule

If a scheduled Phase 15 run is assigned one owning lane, keep the work inside that packet plus the smallest unavoidable shared touch.

If `P15-Y06` is assigned, do not consume packet-local backlog just because the shared sequencing lane has spare room.
