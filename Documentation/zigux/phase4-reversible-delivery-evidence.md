# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reversible on current `master` without reopening starter implementation or widening local-only perf policy into shared CI approval.

## Status
- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`
- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`
- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
- `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
- `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
- `PHASE4_REVERSIBLE_DELIVERY_SHARED_NOTE_BLOB_SHA=76623c6dd1d18742e9d9b7068a06e25126629858`
- `PHASE4_REVERSIBLE_DELIVERY_MATRIX_BLOB_SHA=e83166df5ff8ca637a036d32253eb0bb43d8a972`
- `PHASE4_REVERSIBLE_DELIVERY_REMAINING_GAP_CHECKER_BLOB_SHA=872ada2cfdc25d4eb0c6fa7e912a86c161b5f195`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=280cc852d3d97a2ca97d67f178e092a8bbcf2cda`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=29d118377f7e48125ddccf19fa34364a8d446b51`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=f3dc7b173b7585cbd4cfe9482161e3944d51ce50`
- `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=6d9d5779c8497f4bf6c215e49b0910af6d48b21c`
- `PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=a2e430b4d8bb5e1b6e8cd67e07872d3a8d4f9dcf`

## Current Packet

Treat the following as the current reversible-delivery packet for the already shipped Phase 4 rollback-readiness work:

- shared exact-readback and owner-map evidence:
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  - `Documentation/zigux/review-checklist.md`
- dedicated local-only perf packet:
  - `scripts/zigux/check-phase4-perf-baseline-packet.py`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
- anti-overlap boundary:
  - `Documentation/zigux/phase4-validation-lane-sequencing.md`

The shared note and matrix keep the rollback-owner map, exact-readback packet, parked starter-gap posture, and shared replay-route boundary explicit. The dedicated local-only perf checker, manifest, and survey keep the approved local benchmark commands, approved local-only acceptable limits, and still-pending shared-CI promotion posture measurable without turning that local packet into a shared CI claim.

## Owner Split

Use the current owner split exactly as shipped:

- `Tooling and Validation Team` owns the shared exact-readback wording and the remaining-gap checker packet.
- `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
- `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.

## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.

- If the rollback-owner map, exact-readback wording, or remaining-gap matrix wording drifts, repair the shared exact-readback packet first.
- If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first.
- If a later lane needs both, land the packet-local repair first, then refresh the shared exact-readback note only after the packet-local state is directly readable on current `master`.
- Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
- Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.

## Next Bounded Step

Use this note only as a current-head handoff for already landed work. If this packet reopens, the next honest same-family follow-through is one shared-note truthfulness repair that keeps the exact-readback packet, the dedicated local-only perf packet, and the sequencing note aligned without widening into validator rewrites or starter implementation.
