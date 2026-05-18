# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reviewable on current `master` without reopening starter implementation or widening the dedicated local-only perf packet into shared CI approval.
## Status
  * `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_requires_partial_repo_reality_recheck`
  * `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L24`
  * `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-18`
  * `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
  * `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_NOTE_BLOB_SHA=3a9ec33876a9308ee0a27ad2b9966e73132d7027`
  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=df4a7ab61b728e64b169bf02d4e30ef4ebe1220e`
  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=048f6b9dee482026748e5b9fa6be77a03f4fb2f4`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=4d59621b53f6815a976423b5fbf2318ace438a99`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=44955f39e37b9389b3b97e7d710c25b1841aedf3`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=2e7b03fa41b7fe705ce73158b55249c729caa2fd`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=57ecc3199ca4608828771456f8b6c417c4ab9f1c`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=e6501c3281cc7adaab44e10c600dd52865f024c7`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=20327887d490ac94feda047293e0ba320aabe3a5`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=03388832fabf4353f145007cf68bf5bd56ae28d0`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=5a37abd5f8c02414c9ca8e9d24043a8e8e29f428`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=049c1f90422a49ea83b5e50bf9f9fde9aa5bb501`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=2e16726fec8500136f25afae73e415dbc977faa7`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=12`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`
## Current Packet

Treat this note as the current shared handoff for the Phase 4 rollback-readiness packet, not as proof that every older companion pin in the status block has already been refreshed from live exact blob capture.

Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.

Current direct-readback packet members:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase4-repo-reality-warning.py`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`

Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`.

Current direct-readback dedicated local-only perf companion members:
  * `zigux/tests/phase4_perf_baseline_manifest.json`
  * `zigux/tests/phase4_perf_baseline_survey.zig`

Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.

Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` on current `master`, so the broader review packet has partially recovered past the older all-missing state even though the coupled checker, validator, build, and bitmap replay companions have not all returned through authenticated direct reads yet.

The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=12` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here, so future exact-readback passes can fail closed on stale checker-coverage claims as well as stale packet-member claims.

The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run: authenticated contents reads returned missing for `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`.

The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain mixed provenance in this handoff: current-head proof for the now-directly-readable gate-evidence and validation-matrix notes, and historical provenance for the still-missing checker, validator, build, and bitmap replay companions.

Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here.

Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence even while the broader checker, validator, build, and bitmap replay companions stay in the authenticated-readback gap bucket.

The shared reminder surfaces in `Documentation/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still need a same-family follow-up so they stop overstating `Documentation/zigux/phase4-gate-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` as missing-current-head companions.

Historical broader validator and owner-map packet members:
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

Use this note as the bounded rollback-ownership handoff until the broader packet returns or is republished. The current direct readback now keeps the rollback-owner reminder, the review-checklist handoff, the tests-root route inventory, the repo-reality warning checker, the dedicated pin checker, the dedicated local-only perf packet, the roadmap-backed atomic64 differential-gate pair, and the directly readable gate-evidence plus validation-matrix notes explicit without pretending that the broader checker, validator, build, or bitmap replay companions are presently readable on current `master`.

The shared packet is still supposed to keep the host-side artifact-diff tooling contract, the rollback-owner map, the lab-matrix rows for the parked starter gaps and the local-only perf-threshold posture, and the validator-first replay routes explicit. The dedicated local-only perf checker, manifest, and survey now define the approved local benchmark commands, the approved local-only acceptable limits, and the still-pending shared-CI promotion posture, but this note should not claim current-head readability for the broader checker, validator, build, or bitmap replay packet members until a same-family lane rereads or republishes them.
## Owner Split

Use the current owner split exactly as shipped:
  * `Tooling and Validation Team` owns the shared exact-readback wording, the host-side artifact-diff tooling packet, the lab-matrix note, the remaining-gap checker packet, the tests-root route-inventory truthfulness, the repo-reality warning checker, the dedicated exact-pin checker, the direct-readback dedicated local-only perf checker, and the validator-first route inventory for the Phase 4 packet.
  * `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
  * `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.
## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.
  * If the directly readable repo-reality warning packet drifts, repair the directly readable packet member first and then refresh this note.
  * If a currently readable broader note companion such as `Documentation/zigux/phase4-gate-evidence.md` or `Documentation/zigux/phase4-validation-matrix.md` drifts, refresh the exact pin after rereading the current `master` copy and keep that recovery explicit here without pretending the still-missing checker, validator, build, or bitmap replay companions also returned.
  * If the broader checker, validator, build, or bitmap replay packet returns, refresh the exact pin after rereading the current `master` copy. Until then, keep the corresponding `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance fields historical rather than mixing them into current-head proof.
  * If the roadmap-backed `atomic64_diff` pair drifts again, refresh the direct-readback posture only after re-reading those exact current `master` paths and only after the shared reminder surfaces stop overstating that pair as missing destinations.
  * If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first and then return here only after those packet members are directly readable again.
  * If a later lane needs both, land the packet-local repair first, then refresh this note only after the packet-local state is directly readable on current `master`.
  * Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
  * Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.
## Next Bounded Step

Use this note only as a truthful current-head handoff for the directly readable reminder surfaces and the partially recovered broader notes. The next honest same-family follow-through is a shared-summary truthfulness pass for `Documentation/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md`, followed later by any republish or reread that restores the still-missing broader checker, validator, build, and bitmap replay companions to direct current-head evidence.