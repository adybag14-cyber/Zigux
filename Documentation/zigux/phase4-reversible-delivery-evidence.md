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
  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=7f052e75fdf40fb13f0b95d813969dea43fb4c63`
  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=4d5b5dbc2651caf659a903b6d2ae132e8b26b47c`
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
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=2e16726fec8500136f25afae73e415dbc977faa7`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`
## Current Packet

Treat this note as the current shared handoff for the Phase 4 rollback-readiness packet, not as proof that every older companion pin in the status block has already been refreshed from live exact blob capture.

Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` on current `master`.

Current direct-readback packet members:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase4-repo-reality-warning.py`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`

The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here, so future exact-readback passes can fail closed on stale checker-coverage claims as well as stale packet-member claims.

The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run: authenticated contents reads returned missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`. Public current-`master` fallback readback still exposes those broader companions, so keep the shared owner map narrow until authenticated exact reads recover instead of treating public fallback visibility as current direct-readback proof. The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.

Historical broader packet references still include `scripts/zigux/artifact_diff.py` and `scripts/zigux/check-artifact-diff-contract.py`, so the shared repo-reality warning must keep those contract anchors explicit even while the broader packet stays historical here.

Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` also return missing on current `master`, even though public current-`master` fallback readback still exposes those roadmap-backed differential-gate destinations. Keep that pair parked as authenticated-readback repo-reality gaps instead of listing them as current direct-readback packet members.

The tests-root guide already keeps the broader packet missing-warning aligned, but it does not yet mirror the difference between authenticated direct-readback gaps and public current-`master` fallback visibility. Keep the Phase 4 repo-reality warning in `zigux/tests/README.md` open until that broader validator, lab-matrix, local-only perf, and bitmap-diff packet is directly readable again, and keep the roadmap-backed `atomic64_diff` pair framed as missing current-head destinations until a same-family lane republishes them. The next same-family follow-through inside this live warning packet is therefore either one tests-root wording sync for that fallback-visibility distinction or one checker repair that fails closed on that distinction before any fresh exact-pin pass against still-missing companions.

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

Historical dedicated local-only perf packet members:
  * `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * `zigux/tests/phase4_perf_baseline_manifest.json`
  * `zigux/tests/phase4_perf_baseline_survey.zig`

Last-known anti-overlap boundary:
  * `Documentation/zigux/phase4-validation-lane-sequencing.md`

Use this note as the bounded rollback-ownership handoff until the broader packet returns or is republished. The current direct readback now keeps the rollback-owner reminder, the review-checklist handoff, the tests-root route inventory, the repo-reality warning checker, and the dedicated pin checker explicit without pretending that the broader validator, lab-matrix, local-only perf companions, the bitmap-diff companions, or the roadmap-backed `atomic64_diff` pair are presently readable on current `master`.

The shared packet is still supposed to keep the host-side artifact-diff tooling contract, the rollback-owner map, the lab-matrix rows for the parked starter gaps and the local-only perf-threshold posture, and the validator-first replay routes explicit. The dedicated local-only perf checker, manifest, and survey still define the approved local benchmark commands, the approved local-only acceptable limits, and the still-pending shared-CI promotion posture, but this note should not claim current-head readability for those packet members until a same-family lane rereads or republishes them.
## Owner Split

Use the current owner split exactly as shipped:
  * `Tooling and Validation Team` owns the shared exact-readback wording, the host-side artifact-diff tooling packet, the lab-matrix note, the remaining-gap checker packet, the tests-root route-inventory truthfulness, the repo-reality warning checker, the dedicated exact-pin checker, and the validator-first route inventory for the Phase 4 packet.
  * `Validation and Perf Team` owns the dedicated local-only perf packet and any future broader perf-promotion decision.
  * `ABI and Runtime Team` plus `Shared Subsystems Pod` remain the coordination owners for any wider shared-CI perf promotion because the current landed rollback gates still belong to those families.

Keep the parked starter-gap packets for `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` adjacent but separate. They remain measurable through their own parked survey packets and should not be used as the place to rewrite the shared exact-readback packet or the dedicated local-only perf packet.
## Review Rules

When Phase 4 follow-through reopens, repair the smallest packet that drifted first.
  * If the directly readable repo-reality warning packet drifts, repair the directly readable packet member first and then refresh this note.
  * If the broader validator, lab-matrix, or local-only perf packet returns, refresh the exact pin after re-reading the current `master` copy. Until then, keep the `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance fields historical rather than mixing them into current-head proof.
  * If public fallback still exposes a broader companion while authenticated contents reads do not, refresh the shared reminder wording first and keep the broader packet historical for direct-readback ownership until the authenticated route recovers.
  * If the roadmap-backed `atomic64_diff` pair returns, refresh the direct-readback posture only after re-reading those exact current `master` paths and only after the tests-root warning surface stops treating them as missing destinations.
  * If the local benchmark commands, acceptable limits, or shared-CI-pending posture drifts, repair the dedicated local-only perf packet first and then return here only after those packet members are directly readable again.
  * If a later lane needs both, land the packet-local repair first, then refresh this note only after the packet-local state is directly readable on current `master`.
  * Do not treat the dedicated local-only perf packet as shared CI perf approval until a later bounded Phase 4 lane intentionally widens that policy and names the decision directly.
  * Do not treat either parked starter-gap packet as shipped starter work while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.
## Next Bounded Step

Use this note only as a truthful current-head handoff for the directly readable reminder surfaces. The next honest same-family follow-through is to repair the smallest repo-reality-warning packet drift first, republish one missing broader companion, or restore the roadmap-backed `zigux/tests/atomic64_diff.zig` pair, so this handoff can eventually replace the current `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` provenance with fresh current-head evidence.
