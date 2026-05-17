# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reviewable on current `master` without reopening starter implementation or widening the dedicated local-only perf packet into shared CI approval.
## Status
  * `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_requires_repo_reality_recheck`
  * `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`
  * `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-17`
  * `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
  * `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_NOTE_BLOB_SHA=9c7f55c27720dc28233c5d9aa2bb957c60698d98`
  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=ee2cdde20d4986dae7529dce41b93d00e8c1149e`
  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=3434612a309f81838dcdb44e21040f25f9572f8f`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=0299aa4931145ade8ff83ae05ad640f357c8deda`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=cb8ffe99a6f26f7665eaaf2cbf1d36ecd4de1568`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=2e7b03fa41b7fe705ce73158b55249c729caa2fd`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=57ecc3199ca4608828771456f8b6c417c4ab9f1c`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=e6501c3281cc7adaab44e10c600dd52865f024c7`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=20327887d490ac94feda047293e0ba320aabe3a5`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=c48712a6f5a662e8d45baddcce09ea6f65328224`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=c9fa8b2021a66cd244d1e47feeb9871d9bc327a8`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=98010ca557a586fe12cd770458e27c94b5ef0813`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=a73dc68c02aadcb272bfec8067fbf0120675108c`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=false`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=0`
## Current Packet

Treat this note as the current shared handoff for the Phase 4 rollback-readiness packet, not as proof that every older companion pin in the status block has already been refreshed from live exact blob capture.

Current direct readback in this run confirmed only this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py` on current `master`. Repeated authenticated contents reads in the same run returned missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`. The live repo-reality gap in this note is therefore broader than stale blob provenance alone: the `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines still record the older packet membership and should stay framed as historical provenance until a later bounded Phase 4 lane either re-materializes those companions or republishes a smaller current-head packet around what actually remains readable.

The tests-root guide should mirror this same repo-reality warning. If `zigux/tests/README.md` is updated alongside the Phase 4 packet, keep it aligned with the narrow directly readable rollback packet above and keep the missing validator, lab-matrix, anti-overlap, and local-only perf companions explicit as absent current-`master` routes rather than present evidence.

Current directly readable Phase 4 anchors in this run:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py`

Last-known broader shared rollback packet members recorded as historical provenance:
  * `Documentation/zigux/artifact-diff.md`
  * `Documentation/zigux/phase4-gate-evidence.md`
  * `Documentation/zigux/phase4-validation-matrix.md`
  * `scripts/zigux/artifact_diff.py`
  * `scripts/zigux/check-artifact-diff-contract.py`
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  * `scripts/zigux/check-phase4-workflow-route-counts.py`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * `scripts/zigux/validate-phase4.py`
  * `zigux/tests/phase4_build.zig`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`
  * `Documentation/zigux/review-checklist.md`

Last-known dedicated local-only perf packet members recorded as historical provenance:
  * `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * `zigux/tests/phase4_perf_baseline_manifest.json`
  * `zigux/tests/phase4_perf_baseline_survey.zig`

Last-known anti-overlap boundary recorded as historical provenance:
  * `Documentation/zigux/phase4-validation-lane-sequencing.md`

Use this note as the bounded rollback-ownership handoff until the broader packet is either re-materialized or intentionally narrowed from fresh current-head proof. The current direct readback keeps the rollback-owner reminder, the review-checklist handoff, the tests-root route inventory, and one surviving artifact-diff determinism checker explicit while the broader validator, lab-matrix, anti-overlap, and local-only perf companions stay framed as repo-reality gaps rather than present current-`master` routes.

The shared packet is still supposed to keep the host-side artifact-diff tooling contract, the rollback-owner map, the lab-matrix rows for the parked starter gaps and the local-only perf-threshold posture, and the validator-first replay routes explicit. The dedicated local-only perf checker, manifest, and survey still define the approved local benchmark commands, the approved local-only acceptable limits, and the still-pending shared-CI promotion posture, but this note should not claim refreshed exact blob pins or present current-head readability for those packet members until a same-family lane can prove they are materialized again.
## Owner Split

Use the current owner split exactly as shipped:
  * `Tooling and Validation Team` owns the shared exact-readback wording, the host-side artifact-diff tooling packet, the lab-matrix note, the remaining-gap checker packet, the tests-root route-inventory truthfulness, and the validator-first route inventory for the Phase 4 packet.
  * `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
  * `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.
## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.
  * If the rollback-owner map, the host-side artifact-diff wording, exact-readback wording, lab-matrix wording, tests-root route inventory, remaining-gap checker wording, or validator-first route inventory drifts, repair the directly readable packet member first and then refresh this note.
  * If this handoff note records a stale directly readable companion, refresh the exact pin after re-reading the current `master` copy. This run refreshed `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE` while keeping the `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance fields historical because the broader packet is no longer fully readable on current `master`.
  * If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first and then return here only after those packet members are materialized and directly readable again.
  * If a later lane needs both, land the packet-local repair first, then refresh this note only after the packet-local state is directly readable on current `master`.
  * Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
  * Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.
## Next Bounded Step

Use this note only as a current-head handoff for already landed work. The next honest same-family follow-through is to sync the stale Phase 4 prose in `zigux/tests/README.md` to the same repo-reality warning, then leave the lane parked unless a later reread can either re-materialize one missing broader companion or prove another equally small truthfulness repair inside the rollback, matrix, local-only perf, or artifact-diff reminder surfaces.