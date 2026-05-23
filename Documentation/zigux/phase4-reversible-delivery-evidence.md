# Phase 4 Reversible Delivery Evidence

This note records the smallest shared Phase 4 evidence packet that keeps the already-landed rollback-readiness work reviewable on current `master` without reopening starter implementation or widening the dedicated local-only perf packet into shared CI approval.

## Status
  * `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_keeps_archival_self_pins_and_flapping_broader_blob_refresh_debt`
  * `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`
  * `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`
  * `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-22`
  * `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`
  * `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`
  * `PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA=c48b5c3bebf64b2c2374b816be873c9ac319fff7`
  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_PACKET_CHECKER_BLOB_SHA=c2d2e1bd95517b6607169854e10f3a8516e1ad50`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=5d125f0e20b3378b2d5ff1b94d0779557a980cee`
  * `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=da5a889c5cd3b7fb9c98d6789d04ad473564f16c`
  * `PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA=4157319721f7e4847c8072860ba1fd44b0476de8`
  * `PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA=306b824188945a1e197cb08aec13eda3f42b53ea`
  * `PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA=929ebe22494d052da408cf3a5be1de903f18ff24`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=8d301b9acf67d6af1d575e41c1ff033a0f4b8bc1`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=33d4fa1a339ef355621b5596420c5f1601ffe3cd`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=7e3383aa89561dd2eea6d2dd5e2fd225e4613eb1`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=c1fa46fad53adc7327a03fbe12d3510e854e8bfa`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA=ff0ce79cfda11991f7bdbe1ab3b6b9b6145daf3f`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=86f88d03cd82e2e11ea6ed4a02175b77b472fdb4`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=86af6657cf4abec7ed7ca07bec82c051d974e327`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=8c7fdf65ee906111f8d9a1468cb52bfa8d242763`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=7dc51c0c5e7e3a3dbb2e83c1fedc719631c4db55`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=ef0e3d311379ea1b96e515b304f0ad599832148a`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA=8796bb81928a7cfd70e5fd7f12a61063a49e5d0e`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA=d3c784734232d35d744ca5d2a0ea2ea2580524c7`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA=fc353bfc7ecdc4c5e9e064a950c0af1a53591989`
  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=75c533b819a0bb422e69c92a33a23da7c04d5af1`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=20`
  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18`

## Current Packet

Treat this note as the current shared handoff for the Phase 4 rollback-readiness packet, not as proof that every older companion pin in the status block has already been refreshed from live exact blob capture.

Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.

Current direct-readback packet members:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase4-repo-reality-warning.py`
  * `scripts/zigux/check-phase4-tests-readme-packet.py`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`

Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`.

Current direct-readback dedicated local-only perf companion members:
  * `zigux/tests/phase4_perf_baseline_manifest.json`
  * `zigux/tests/phase4_perf_baseline_survey.zig`

Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`, together with the manifest-backed handoff packet `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, on current `master`.

Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts/zigux/validate-phase4.py` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.

The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=20` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=18` here, so future exact-readback passes can fail closed on stale checker-coverage claims as well as stale packet-member claims.

The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff. Direct authenticated contents reads in this runtime now return `scripts/zigux/validate-phase4.py` directly, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap on that same route; public raw fallback rereads continue to return the full set on current `master`, matching the broader review packet's recovered note-and-checker companions.

The recovered broader note pair therefore no longer overstates those validator-side and bitmap-side companions as absent current-head evidence. Treat this narrower handoff as the authoritative shared reminder while exact blob recapture for `scripts/zigux/validate-phase4.py` returns to a direct authenticated pin path and the build and bitmap replay companions still wait on steadier authenticated contents reads.

The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff: current-head proof for the docs-root reminder, the scripts-root reminder, the review checklist, the tests-root reminder, the repo-reality warning checker, the tests-readme packet checker, the reversible-delivery pin checker, the recovered gate-evidence note, validation matrix, validation-lane sequencing note, the recovered gate-evidence and remaining-gap checkers, the workflow-route checker, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the atomic64 manifest-backed survey pair, and the dedicated local-only perf checker plus companion packet; archival anchor pin only for this note's self-reference; current-head direct-readback proof that `scripts/zigux/validate-phase4.py` is present again on `master`; public-raw current-tree proof that `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`; and historical blob-pin provenance for that broader build-and-bitmap trio until exact authenticated blob capture stabilizes.

Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, and `scripts/zigux/check-phase4-artifact-diff-determinism.py`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here.

Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.

The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `scripts/zigux/check-phase4-tests-readme-packet.py` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, the directly returned validator, and the still-public-raw-returned build and bitmap replay companions, while exact blob-pin refresh for that broader packet remains the remaining authenticated-readback gap in this handoff.
