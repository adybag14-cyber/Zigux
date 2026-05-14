# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reversible on current `master` without reopening starter implementation or widening the dedicated local-only perf packet into shared CI approval.

## Status
- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`
- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`
- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-14`
- `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
- `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
- `PHASE4_REVERSIBLE_DELIVERY_GATE_EVIDENCE_BLOB_SHA=95ae13c6ed6b3c728d07f2b7663ba4e63b982d75`
- `PHASE4_REVERSIBLE_DELIVERY_MATRIX_BLOB_SHA=1f94af416592ebc302e27a321a847a5e1c0ee1d7`
- `PHASE4_REVERSIBLE_DELIVERY_REMAINING_GAP_CHECKER_BLOB_SHA=7c6c2e48af10f225fe075d932fe82a2a04e840dd`
- `PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=f272c9bcf0046b3f10f8a47018f3724ddbf1d834`
- `PHASE4_REVERSIBLE_DELIVERY_VALIDATOR_BLOB_SHA=fe74d4b5cf3edeb4afee2abf9c6e07d2472145a3`
- `PHASE4_REVERSIBLE_DELIVERY_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
- `PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA=812e7e708b6c6cf3c2879e12e8ce7c906d5d4069`
- `PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_BLOB_SHA=5d4232d7465c83dcf669d71a4729fc38e986739b`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=4fcf708d0fcdc0d5efe3c4addeb405d0387c78da`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=c9fa8b2021a66cd244d1e47feeb9871d9bc327a8`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=98010ca557a586fe12cd770458e27c94b5ef0813`
- `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=c4fb43918f6a7af05209ac4be1acb896fdf297cf`
- `PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=58921cd0441cb061461a12b22438f2c33decce31`

## Current Packet

Treat the following as the current reversible-delivery packet for the already shipped Phase 4 rollback-readiness work:

- shared exact-readback and owner-map evidence:
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  - `scripts/zigux/check-phase4-workflow-route-counts.py`
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

The shared packet keeps the rollback-owner map, the exact-readback wording, the parked starter-gap posture, and the current validator-first replay routes explicit. The dedicated local-only perf checker, manifest, and survey keep the approved local benchmark commands, the approved local-only acceptable limits, and the still-pending shared-CI promotion posture measurable without turning that local packet into a shared CI claim.

## Owner Split

Use the current owner split exactly as shipped:

- `Tooling and Validation Team` owns the shared exact-readback wording, the remaining-gap checker packet, and the validator-first route inventory for the current shared Phase 4 packet.
- `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
- `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.

## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.

- If the rollback-owner map, exact-readback wording, remaining-gap matrix wording, or validator-first route inventory drifts, repair the shared exact-readback packet first.
- If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first.
- If a later lane needs both, land the packet-local repair first, then refresh the shared exact-readback note only after the packet-local state is directly readable on current `master`.
- Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
- Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.

## Next Bounded Step

Use this note only as a current-head handoff for already landed work. If this packet reopens, the next honest same-family follow-through is one shared-note truthfulness repair that keeps the exact-readback packet, the validator-first route packet, the dedicated local-only perf packet, and the sequencing note aligned without widening into starter implementation or shared CI perf promotion.
