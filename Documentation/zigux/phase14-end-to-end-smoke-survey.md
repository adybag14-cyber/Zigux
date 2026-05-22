# Phase 14 End-to-End Smoke Survey

This document records the shared Phase 14 smoke lane that keeps the current bounded-internals evidence bundle reviewable on `master`.

## Status
  * `PHASE14_STATUS=active`
  * `PHASE14_SLICE=end-to-end-smoke-verification`
  * `PHASE14_DIRECT_DOC_PACKET=present`
  * `PHASE14_EXECUTABLE_PACKET_READBACK=partial`
  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`
  * `PHASE14_ANCHOR_PACKET_COUNT=4`
  * `PHASE14_STAY_IN_C_BOUNDARY=explicit`
  * `PHASE14_STATUS_CHANGE_CLAIM=no`
  * refreshed against fresh exact current-`master` contents recovery plus current public-tree smoke-file readback on `2026-05-22`
  * directly readable shared smoke companions in this lane's contents path:
    * `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
    * `Documentation/zigux/phase14-core-boundary-traceability.md`
    * `Documentation/zigux/phase14-release-boundary-survey.md`
    * `Documentation/zigux/phase14-productization-gap-survey.md`
    * `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`
    * `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`
    * `Documentation/zigux/phase14-skbuff-bridge-survey.md`
    * `Documentation/zigux/freeze-map.md`
    * `Documentation/zigux/README.md`
    * `Documentation/zigux/review-checklist.md`
    * `Documentation/zigux/phase15-study-only-anchor-accounting.md`
  * directly readable current-`master` companion surfaces in this lane's current evidence split:
    * `scripts/zigux/check-phase14-shared-smoke-route.py` through the current contents path
    * `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` through the current contents path
    * `scripts/zigux/validate-phase14.py` through the current contents path
    * `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` through the current contents path
    * `scripts/zigux/check-phase14-release-boundary-exact-counts.py` through the current contents path
    * `zigux/Makefile` through the current contents path
    * `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path
  * directly readable anchor-local workqueue boundary shard in this lane's current evidence split:
    * `kernel/workqueue_bridge.zig`
    * `zigux/tests/phase14_workqueue_bridge.zig`
    * `zigux/tests/phase14_workqueue_reviewability.zig`
    * `zigux/tests/phase14_workqueue_bridge_manifest.json`
  * directly readable ring-buffer survey companion in this lane's current evidence split:
    * `zigux/tests/phase14_ring_buffer_survey.zig`
  * executable packet members still unrecovered through this lane's exact contents path:
    * `zigux/tests/phase14_build.zig`
    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`
    * `zigux/tests/phase14_skbuff_bridge.zig`
    * `zigux/tests/phase14_rcu_tree_survey.zig`
    * `net/core/skbuff_bridge.zig`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 still needs a small shared smoke packet that keeps those four anchors reviewable as one bounded evidence bundle instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It records the directly readable shared-smoke documentation layer, keeps the attached-toolchain boundary explicit for the bounded rerun routes historically named here, keeps the directly readable shared-smoke route guard, tests-root reminder guard, validator, rollback-threshold sequencing guard, and release-boundary guard visible, keeps the directly readable workqueue reviewability foothold explicit, keeps the directly readable ring-buffer survey foothold explicit, keeps the directly readable shared smoke manifest explicit, and makes the remaining exact-readback gaps explicit instead of overstating repo reality.

## Exact evidence captured
  * directly readable current-`master` documentation layer:
    * the shared smoke survey, release-boundary survey, cross-anchor traceability note, productization-gap note, attached-toolchain guidance gap note, shared-smoke gap note, freeze map, docs-root summary, review checklist, skbuff survey, and Phase 15 study-only accounting companion are all directly readable again through this lane's exact contents path
  * directly readable current-`master` reminder layer:
    * `scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path and now keeps the returned `phase14-validate` Makefile route plus workflow gate explicit instead of leaving that shared route proof implicit in adjacent reminder prose
    * `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` is directly readable again through the current contents path and now keeps the tests-root shared-smoke reminder aligned with the returned route split instead of leaving that narrower tests-surface evidence implicit in neighboring reminder prose
    * `scripts/zigux/validate-phase14.py` is directly readable again through the current contents path and now carries the shared smoke validator surface rather than the older placeholder body
    * `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` is directly readable again through the current contents path and now keeps the shared smoke rollback threshold, fallback path, automatic return-to-blocked triggers, and returned Makefile split explicit instead of leaving that route contract implicit in adjacent reminder prose
    * `scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again through the current contents path and now keeps the release-facing exact-count posture aligned with the returned shared reminder packet
    * `zigux/Makefile` is directly readable again through the current contents path, and its live body now exposes the shipped Phase 2 toolchain and kbuild routes together with the bounded `phase3-validate`, `phase3`, `phase4-validate`, `phase4-test`, `phase4`, `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, `phase12-smoke`, `phase12-test`, `phase12`, and `phase14-validate`, but no `phase14-smoke`, `phase14-test`, or `phase14` targets
    * `zigux/tests/phase14_end_to_end_smoke_manifest.json` is directly readable again through the current contents path, and its live body keeps `make -C zigux phase14-validate` as the only shared smoke Makefile command, records the focused raw build-file smoke shard `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`, and still does not revive `phase14-smoke`, `phase14-test`, or `phase14` as Makefile or workflow-backed coverage
    * that means later same-lane follow-through should only touch the smallest shared reminder surface that drifts against this returned Makefile split, not default back to a validator-local exact-line sync or an already-aligned tests-root rewrite
  * the directly readable rollback-threshold sequencing guard:
    * the current shared smoke packet now has a directly readable rollback-threshold sequencing checker, so later same-lane work should keep rollback-threshold wording aligned with the current route split instead of leaving that contract implicit in neighboring reminder text
  * the directly readable release-boundary exact-count guard:
    * the current shared smoke packet now has a directly readable release-facing exact-count checker, so later same-lane work should keep release-boundary wording aligned with the current route split instead of treating that guard as part of the missing executable layer
  * the directly readable workqueue boundary shard:
    * `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again on current `master`, so the shared smoke packet should keep the workqueue reviewability foothold explicit even while the broader executable layer stays partial
    * workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, current slice `phase14-workqueue-scheduler-visible-worker-state-refinement`, posture `blocked_maintenance`, blocked `phase14-workqueue-live-execution-blocker`
    * `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`
  * the directly readable ring-buffer survey companion:
    * `zigux/tests/phase14_ring_buffer_survey.zig` is directly readable again on current `master`, so the shared smoke packet should keep the study-only ring-buffer survey foothold explicit even while the build-side and broader executable layer stay partial
  * exact-readback gaps that still belong to this shared note:
    * `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` still do not return through this lane's exact contents path
    * broad reminder text should therefore frame that build-side and broader executable layer as exact-readback gaps rather than as directly recovered shared-smoke proof
  * packet-local command posture preserved by this note:
    * the current readable route layer still stops at `make -C zigux phase14-validate`; no current attached-toolchain `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux phase14` fallback is usable from this note because the readable `zigux/Makefile` body still omits those targets
    * the same packet can still name the focused raw build-file shard `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig` as reviewability evidence without promoting it into a returned Makefile wrapper or workflow-backed route
    * keep those older wrapper names recorded only as historical packet vocabulary until the same exact readback mode restores the missing broader Phase 14 Makefile routes on current `master`
  * current anchor posture reflected by the recovered documentation packet:
    * workqueue remains `Study / Boundary Only`
    * skbuff remains `Freeze In C Initially` and parked on `phase14-skbuff-live-ownership-blocker`
    * ring buffer remains `Study / Boundary Only`
    * RCU tree remains `Freeze In C Initially`

## Shared smoke findings
  * directly readable current-`master` evidence is no longer a docs-level absence of the shared smoke packet; the documentation layer is recoverable again through this lane's exact contents path
  * `scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path and exposes the current shared `phase14-validate` route proof, so this note must stop leaving that route evidence implicit in adjacent reminder prose
  * `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` is directly readable again through the current contents path and exposes the current tests-root shared-smoke reminder guard, so this note must stop leaving that narrower tests-surface evidence implicit in neighboring reminder prose
  * `scripts/zigux/validate-phase14.py` is directly readable again through the current contents path and exposes a real shared-smoke validator surface, so this note must stop treating the returned path as a blob-readable mixed-source companion
  * `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` is directly readable again through the current contents path and exposes the current rollback-threshold sequencing packet, so this note must stop leaving that route contract implicit in adjacent reminder prose
  * `scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again too, so this note must stop treating the release-facing exact-count guard as part of the unrecovered executable layer
  * `zigux/Makefile` is readable again too, and the current returned file body now exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `phase14-validate` gate, but it still does not ship the older `phase14-smoke`, `phase14-test`, or `phase14` rerun routes named by earlier shared reminder text
  * `zigux/tests/phase14_end_to_end_smoke_manifest.json` is directly readable again through the current contents path, so the machine-readable shared smoke surface inventory and compile-shard catalog are part of current evidence rather than an exact-readback gap; the same manifest now records the focused raw build-file smoke shard while still keeping wrapper-backed rerun coverage absent
  * the directly readable workqueue boundary shard remains part of current-`master` evidence: `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the study-only `kernel/workqueue.c` anchor reviewable as a boundary-map-and-reviewability foothold even while the broader shared executable layer stays partial
  * the directly readable ring-buffer survey companion is part of current-`master` evidence too: `zigux/tests/phase14_ring_buffer_survey.zig` keeps the study-only `kernel/trace/ring_buffer.c` anchor reviewable as a focused survey foothold even while the broader shared executable layer stays partial
  * the remaining shared-smoke risk is route-layer mismatch across the surviving reminder surfaces. Docs-root, checklist, scripts-root, tests-root, release-boundary, productization-gap, shared-gap, attached-toolchain notes, and the directly readable rollback-threshold sequencing checker should all keep the returned `phase14-validate` gate, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the exact-readback-gap posture, and the focused raw build-file smoke shard aligned instead of implying a broader current-`master` replay
  * the broader repo-reality gap is now narrower: the shared smoke packet has readable documentation, shared-smoke route proof, tests-root reminder proof, validator, rollback-threshold sequencing, release-boundary, shared smoke manifest, workqueue reviewability, and ring-buffer survey surfaces again, but the build-side and broader executable layer are still exact-readback gaps in this lane
  * the attached-toolchain boundary still belongs here, but only as a truthfulness guard: while `zigux/Makefile` lacks `phase14-smoke`, `phase14-test`, and `phase14`, this note should not offer wrapper-backed attached-toolchain reruns for those targets as if they are currently executable in the recovered packet
  * some shared reminder surfaces may still lag this current route split, so same-lane follow-through should tighten the smallest stale note next instead of sending the lane back toward an already-closed validator-local handoff or an anchor-local reopen
  * all four anchor families remain parked on study-only or freeze-in-C posture, so no anchor-local reopen is justified from this shared note alone

## Productization evidence
  * named owner: `Core-Adjacent Pod`
  * status bucket: `study_only`
  * evidence mode: `documentation_layer_plus_direct_route_and_tests_reminder_guards_plus_direct_validator_and_rollback_and_release_guards_plus_workqueue_boundary_shard_plus_ring_buffer_survey_companion_exact_readback_gaps_for_build_side_and_broader_executable_layer`
  * rollback owner: `Repo Tooling Pod`
  * rollback threshold: `0` tolerated same-packet drifts across the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable validator path, the directly readable rollback-threshold sequencing checker, the readable current Makefile body, the directly readable release-boundary exact-count guard, the directly readable workqueue boundary shard, the directly readable ring-buffer survey companion, the directly readable shared smoke manifest, and the still-missing broader wrapper-backed rerun routes
  * fallback path: keep this shared smoke lane aligned with the current gap notes until the broader shared reminder packet stops treating the current Makefile body as if it still shipped `phase14-smoke`, `phase14-test`, and `phase14`, and until the build-side and broader executable packet members return through exact current-`master` readback; once they do, rerun the packet-local commands below before restoring any stronger validator-first claim
  * automatic return-to-blocked triggers:
    * recovered documentation packet drift
    * route-checker-versus-reminder-surface drift
    * tests-root-checker-versus-reminder-surface drift
    * validator-versus-reminder-surface drift
    * rollback-threshold-sequencing drift
    * workqueue-boundary-shard drift
    * ring-buffer-survey drift
    * wrapper-route drift
    * build-side exact-readback-gap drift
    * broader executable-layer exact-readback-gap drift
    * attached-toolchain guidance drift inside the shared smoke note
  * ZAR-to-product transfer rationale: absorb ZAR runtime research as product discipline only by keeping exported evidence notes, exact readback truthfulness, explicit blocker posture, bounded rerun guidance, directly readable shared smoke manifest evidence, directly readable rollback-threshold sequencing evidence, and directly readable anchor-local boundary shards visible without turning partial readback into a parity or ownership claim

## Non-goals

This shared smoke slice does not claim:

  * live workqueue execution, draining, or cancellation parity
  * skbuff lifetime, destructor, checksum, or segmentation ownership
  * `kernel/trace/ring_buffer.zig`
  * `kernel/rcu/tree_bridge.zig`
  * any new focused replay route for the four anchor-local packets
  * any direct current-`master` build-backed proof beyond the recovered documentation layer, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable validator path, the directly readable rollback-threshold sequencing checker, the readable Makefile body with its shipped non-Phase-14 routes, the directly readable release-boundary exact-count guard, the directly readable shared smoke manifest, the directly readable workqueue boundary shard, the directly readable ring-buffer survey companion, and the still-partial wrapper-backed rerun family
  * any Phase 14 status change beyond keeping the current evidence packet truthful

## Packet-Local Rerun Vocabulary

This lane now treats `make -C zigux phase14-validate` as current rerun guidance because the readable `zigux/Makefile` body exposes that route and the returned target reruns `scripts/zigux/check-phase14-shared-smoke-route.py --self-test`, `scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/validate-phase14.py --self-test`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`.

The same lane also keeps `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig` explicit as the focused raw build-file shard recorded by the shared smoke manifest.

Keep `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase14`, and the attached-toolchain `ZIG=/absolute/path/to/attached-zig/zig ...` variants only as historical packet vocabulary until the same exact readback mode restores the missing broader Makefile routes on current `master`.

## Next bounded step

Keep this core-adjacent lane focused on shared reminder truthfulness until the broader wrapper-backed Phase 14 rerun family and the exact-readback-gap build-side pair return.

If a future same-lane reread still finds the readable `zigux/Makefile` body exposing `phase14-validate` but still lacking `phase14-smoke`, `phase14-test`, and `phase14`, publish only the smallest shared reminder repair that falls out of alignment with that returned route split before reopening any validator-local handoff.

If a future same-lane reread regains exact current-`master` contents readback for `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, or `net/core/skbuff_bridge.zig` while the broader wrapper layer remains partial, keep this note, `Documentation/zigux/phase14-core-boundary-traceability.md`, and the surviving shared reminder packet aligned so the returned build-side or anchor-local footholds become explicit without overstating broader replay proof.

If the docs-root, checklist, scripts-root, tests-root, release-boundary, productization-gap, shared-gap, or attached-toolchain reminder surfaces are edited first, keep them aligned with the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable validator path, the directly readable rollback-threshold sequencing checker, the readable Makefile body with its shipped non-Phase-14 routes, the directly readable release-boundary exact-count guard, the directly readable shared smoke manifest, the directly readable workqueue boundary shard, the directly readable ring-buffer survey companion, and the still-partial wrapper layer instead of implying a broader current-`master` replay.

## Footer