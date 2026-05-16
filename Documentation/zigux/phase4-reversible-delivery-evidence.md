# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reversible on current `master` without reopening starter implementation or widening the dedicated local-only perf packet into shared CI approval.

## Status
- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`
- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`
- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-16`
- `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
- `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
- `PHASE4_REVERSIBLE_DELIVERY_GATE_EVIDENCE_BLOB_SHA=e348d0890217e3bdca98c5ba6915fd343060f699`
- `PHASE4_REVERSIBLE_DELIVERY_MATRIX_BLOB_SHA=d73679558764fcdd3fcc9962c59d4e28bf3a3b6f`
- `PHASE4_REVERSIBLE_DELIVERY_REMAINING_GAP_CHECKER_BLOB_SHA=2e7b03fa41b7fe705ce73158b55249c729caa2fd`
- `PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=57ecc3199ca4608828771456f8b6c417c4ab9f1c`
- `PHASE4_REVERSIBLE_DELIVERY_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
- `PHASE4_REVERSIBLE_DELIVERY_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
- `PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA=5da552c676a6522e5494b3c24fcffab647cef893`
- `PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_BLOB_SHA=20327887d490ac94feda047293e0ba320aabe3a5`
- `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=dc7ecae5af43699886227cce44bf20dcf161c4df`
- `PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=a73dc68c02aadcb272bfec8067fbf0120675108c`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=c48712a6f5a662e8d45baddcce09ea6f65328224`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=c9fa8b2021a66cd244d1e47feeb9871d9bc327a8`
- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=98010ca557a586fe12cd770458e27c94b5ef0813`
- `PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_NOTE_BLOB_SHA=23ce608d32537a74b357770647c0850cdcd760ce`
- `PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_MANIFEST_BLOB_SHA=6a285bdccdfe4b1874340f9e264d1543c9c103b9`
- `PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_SURVEY_BLOB_SHA=a7648edec611679ee2ba51d0a410a153b7bfac46`
- `PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_NOTE_BLOB_SHA=23eb282bbdf3fe4ed73b4f29cbcadd2a081ff77f`
- `PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_MANIFEST_BLOB_SHA=2161e2ff2dd413dc54a9a83f224ba995c03e0519`
- `PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_SURVEY_BLOB_SHA=052f17a4938995eaf97ed256411f0021103459b9`
- `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
- `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=41`

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
- dedicated parked kprobe reversible-delivery packet:
  - `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
  - `zigux/tests/phase4_kprobe_example_manifest.json`
  - `zigux/tests/phase4_kprobe_example_survey.zig`
- dedicated parked test_fsmount reversible-delivery packet:
  - `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
  - `zigux/tests/phase4_test_fsmount_manifest.json`
  - `zigux/tests/phase4_test_fsmount_survey.zig`
- anti-overlap boundary:
  - `Documentation/zigux/phase4-validation-lane-sequencing.md`

Use `Documentation/zigux/phase4-gate-evidence.md` as the exact shared blob-pin checkpoint for the already-landed packet. This handoff note now keeps the shared matrix, the remaining-gap checker, the workflow-route checker, the validator-first replay surface, the dedicated local-only perf packet, the dedicated parked kprobe packet, the dedicated parked test_fsmount packet, the review checklist, and the sequencing note readable together as the smallest current reversible-delivery evidence set.

The dedicated `scripts/zigux/check-phase4-reversible-delivery-pins.py` checker now fail-closes on the shared exact-readback packet plus the validator-first, local-only perf, parked kprobe, and parked test_fsmount anchors recorded in this handoff note: `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, so those cross-packet anchors and the parked gap note-manifest-survey handoffs stay exact when the shared exact-readback packet, the validator-first route inventory, the dedicated local-only perf packet, or either parked starter-gap packet moves again.

The shared packet keeps the rollback-owner map, the lab-matrix rows for the parked starter gaps and the local-only perf-threshold posture, and the current validator-first replay routes explicit. The dedicated local-only perf checker, manifest, and survey keep the approved local benchmark commands, the approved local-only acceptable limits, and the still-pending shared-CI promotion posture measurable without turning that local packet into a shared CI claim. The parked kprobe packet keeps the absent starter boundary, the explicit local lab replay marker, the dedicated local survey wrapper, and the direct validation entrypoint measurable through `make -C zigux phase4-kprobe-example-survey` and `zig test zigux/tests/phase4_kprobe_example_survey.zig` without turning that parked packet into shipped starter work. The parked test_fsmount packet keeps the absent starter boundary, both local survey wrappers, and the direct validation entrypoint measurable through `make -C zigux phase4-test-fsmount-survey` and `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` without turning that parked packet into shipped starter work.

## Owner Split

Use the current owner split exactly as shipped:

- `Tooling and Validation Team` owns the shared exact-readback wording, the lab-matrix note, the remaining-gap checker packet, and the validator-first route inventory for the current shared Phase 4 packet.
- `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
- `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.
- the parked `kprobe_example` and `test_fsmount` packets remain adjacent but separate, and the shared handoff note should only name their dedicated notes, manifests, surveys, current local replay routes, and direct validation entrypoints instead of restating packet-local behavior from memory.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.

## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.

- If the rollback-owner map, exact-readback wording, lab-matrix wording, remaining-gap checker wording, or validator-first route inventory drifts, repair the shared exact-readback packet first.
- If the shared exact-readback packet, validator-first route inventory, `Documentation/zigux/phase4-validation-lane-sequencing.md`, or dedicated local-only perf packet blob pins drift inside this handoff note, repair this note together with `scripts/zigux/check-phase4-reversible-delivery-pins.py` after the directly readable current-head file change lands on `master`.
- If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first.
- If the parked `kprobe_example` packet's local replay marker, local survey wrapper, direct validation entrypoint, or absent-starter boundary drifts, repair the parked kprobe packet first and refresh this handoff note only if its shared reference now drifts.
- If the parked `test_fsmount` packet's local replay marker, local survey wrappers, direct validation entrypoint, or absent-starter boundary drifts, repair the parked test_fsmount packet first and refresh this handoff note only if its shared reference now drifts.
- If a later lane needs both, land the packet-local repair first, then refresh the shared exact-readback note only after the packet-local state is directly readable on current `master`.
- Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
- Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.

## Next Bounded Step

Use this note only as a current-head handoff for already landed work. If this packet reopens, the next honest same-family follow-through is one shared-note truthfulness repair that keeps the exact-readback packet, the lab-matrix packet, the dedicated local-only perf packet, the parked kprobe packet, the parked test_fsmount packet, and the sequencing note aligned without widening into starter implementation or shared CI perf promotion.
