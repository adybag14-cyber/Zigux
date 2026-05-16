# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reversible on current `master` without reopening starter implementation or widening the dedicated local-only perf packet into shared CI approval.

## Status
- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`
- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`
- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-16`
- `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
- `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
- `PHASE4_REVERSIBLE_DELIVERY_GATE_EVIDENCE_BLOB_SHA=62262fc0726f7a313c648490620dbee7f2899646`
- `PHASE4_REVERSIBLE_DELIVERY_MATRIX_BLOB_SHA=8c458d2495f109fb58f2d9a719a69a790b0a071e`
- `PHASE4_REVERSIBLE_DELIVERY_REMAINING_GAP_CHECKER_BLOB_SHA=8df4ba9d8129ed52b3327226eb82f5f9de1f0e90`
- `PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=5b512de0fe54383c46074b699a23dcc0b7a86648`
- `PHASE4_REVERSIBLE_DELIVERY_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
- `PHASE4_REVERSIBLE_DELIVERY_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
- `PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA=e6501c3281cc7adaab44e10c600dd52865f024c7`
- `PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_BLOB_SHA=20327887d490ac94feda047293e0ba320aabe3a5`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=c48712a6f5a662e8d45baddcce09ea6f65328224`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=c9fa8b2021a66cd244d1e47feeb9871d9bc327a8`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=98010ca557a586fe12cd770458e27c94b5ef0813`
- `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=c70dfd75d82cfb15cf4b59f0e547cdfa0000ee2f`
- `PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=eb190d81c7590e33fd4c40b1feaf0bd39e93467b`
- `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
- `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=29`

## Current Packet

Treat the following as the current reversible-delivery packet for the already shipped Phase 4 rollback-readiness work:

- shared exact-readback and owner-map evidence:
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  - `scripts/zigux/check-phase4-workflow-route-counts.py`
  - `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  - `scripts/zigux/validate-phase4.py`
  - `zigux/tests/phase4_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `Documentation/zigux/review-checklist.md`
- dedicated local-only perf packet:
  - `scripts/zigux/check-phase4-perf-baseline-packet.py`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
- anti-overlap boundary:
  - `Documentation/zigux/phase4-validation-lane-sequencing.md`

Use `Documentation/zigux/phase4-gate-evidence.md` as the exact shared blob-pin checkpoint for the already-landed packet. This handoff note now keeps the shared matrix, the remaining-gap checker, the workflow-route checker, the validator-first replay surface, the dedicated local-only perf packet, the review checklist, and the sequencing note readable together as the smallest current reversible-delivery evidence set.

The dedicated `scripts/zigux/check-phase4-reversible-delivery-pins.py` checker now fail-closes on the shared exact-readback packet plus validator-first and local-only perf anchors recorded in this handoff note: `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`, so those cross-packet anchors stay exact when the shared exact-readback packet, the validator-first route inventory, or the dedicated local-only perf packet moves again.

The shared packet keeps the rollback-owner map, the lab-matrix rows for the parked starter gaps and the local-only perf-threshold posture, and the current validator-first replay routes explicit. The dedicated local-only perf checker, manifest, and survey keep the approved local benchmark commands, the approved local-only acceptable limits, and the still-pending shared-CI promotion posture measurable without turning that local packet into a shared CI claim.

## Owner Split

Use the current owner split exactly as shipped:

- `Tooling and Validation Team` owns the shared exact-readback wording, the lab-matrix note, the remaining-gap checker packet, and the validator-first route inventory for the current shared Phase 4 packet.
- `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
- `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.

## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.

- If the rollback-owner map, exact-readback wording, lab-matrix wording, remaining-gap checker wording, or validator-first route inventory drifts, repair the shared exact-readback packet first.
- If the shared exact-readback packet, validator-first route inventory, `Documentation/zigux/phase4-validation-lane-sequencing.md`, or dedicated local-only perf packet blob pins drift inside this handoff note, repair this note together with `scripts/zigux/check-phase4-reversible-delivery-pins.py` after the directly readable current-head file change lands on `master`.
- If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first.
- If a later lane needs both, land the packet-local repair first, then refresh the shared exact-readback note only after the packet-local state is directly readable on current `master`.
- Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
- Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.

## Next Bounded Step

Use this note only as a current-head handoff for already landed work. If this packet reopens, the next honest same-family follow-through is one shared-note truthfulness repair that keeps the exact-readback packet, the lab-matrix packet, the dedicated local-only perf packet, and the sequencing note aligned without widening into starter implementation or shared CI perf promotion.