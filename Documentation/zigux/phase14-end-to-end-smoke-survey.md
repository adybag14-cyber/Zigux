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
  * refreshed against fresh exact current-`master` contents recovery on `2026-05-18`
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
  * directly readable mixed-source companions in this lane's current evidence split:
    * `scripts/zigux/validate-phase14.py` through pinned blob readback
    * `scripts/zigux/check-phase14-release-boundary-exact-counts.py` through the current contents path
    * `zigux/Makefile` through the current contents path
  * directly readable anchor-local workqueue boundary shard in this lane's current evidence split:
    * `kernel/workqueue_bridge.zig`
    * `zigux/tests/phase14_workqueue_bridge.zig`
    * `zigux/tests/phase14_workqueue_reviewability.zig`
    * `zigux/tests/phase14_workqueue_bridge_manifest.json`
  * executable packet members still unrecovered through this lane's exact contents path:
    * `zigux/tests/phase14_build.zig`
    * `zigux/tests/phase14_end_to_end_smoke_manifest.json`
    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`
    * `zigux/tests/phase14_skbuff_bridge.zig`
    * `zigux/tests/phase14_ring_buffer_survey.zig`
    * `zigux/tests/phase14_rcu_tree_survey.zig`
    * `net/core/skbuff_bridge.zig`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 still needs a small shared smoke packet that keeps those four anchors reviewable as one bounded evidence bundle instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It records the directly readable shared-smoke documentation layer, keeps the attached-toolchain boundary explicit for the bounded rerun routes historically named here, and makes the remaining executable-layer readback gap explicit instead of overstating repo reality.

## Exact evidence captured
  * directly readable current-`master` documentation layer:
    * the shared smoke survey, release-boundary survey, cross-anchor traceability note, productization-gap note, attached-toolchain guidance gap note, shared-smoke gap note, freeze map, docs-root summary, review checklist, skbuff survey, and Phase 15 study-only accounting companion are all directly readable again through this lane's exact contents path
  * directly readable mixed-source reminder layer:
    * `scripts/zigux/validate-phase14.py` is recoverable again through pinned blob readback and now carries the shared smoke validator surface rather than the older placeholder body
    * `scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again through the current contents path and now keeps the release-facing exact-count posture aligned with the returned shared reminder packet
    * `zigux/Makefile` is directly readable again through the current contents path, and its live body now exposes the shipped Phase 2 toolchain and kbuild routes together with the bounded `phase3-validate`, `phase3`, `phase4-validate`, `phase4-test`, `phase4`, `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, `phase12-smoke`, `phase12-test`, and `phase12`, but no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets
    * that means the next honest same-lane follow-through is reminder-surface truthfulness, not a validator-local exact-line sync against `phase14-validate`
  * directly readable anchor-local workqueue boundary shard:
    * `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again on current `master`, so the shared smoke packet should keep the workqueue reviewability foothold explicit even while the broader executable layer stays partial
    * workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, ready-next `none currently recorded`, blocked `phase14-workqueue-live-execution-blocker`
    * `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`
  * packet-local command posture preserved by this note:
    * no current attached-toolchain `make -C zigux phase14-*` fallback is usable from this note, because the readable `zigux/Makefile` body still omits `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14`
    * keep those older wrapper names recorded only as historical packet vocabulary until the same readback mode restores both the dedicated Phase 14 build files and the `phase14-*` Makefile targets on current `master`
  * current anchor posture reflected by the recovered documentation packet:
    * workqueue remains `Study / Boundary Only`
    * skbuff remains `Freeze In C Initially` and parked on `phase14-skbuff-live-ownership-blocker`
    * ring buffer remains `Study / Boundary Only`
    * RCU tree remains `Freeze In C Initially`

## Shared smoke findings
  * directly readable current-`master` evidence is no longer a docs-level absence of the shared smoke packet; the documentation layer is recoverable again through this lane's exact contents path
  * `scripts/zigux/validate-phase14.py` is also recoverable again through pinned blob readback and exposes a real shared-smoke validator surface, so this note must stop treating the returned path as the older placeholder-only body
  * `scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again too, so this note must stop treating the release-facing exact-count guard as part of the unrecovered executable layer
  * `zigux/Makefile` is readable again too, and the current returned file body now exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes, but it still does not ship the older `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` rerun routes named by earlier shared reminder text
  * the directly readable workqueue boundary shard remains part of current-`master` evidence: `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the study-only `kernel/workqueue.c` anchor reviewable as a boundary-map-and-reviewability foothold even while the broader shared executable layer stays partial
  * the remaining shared-smoke drift is therefore reminder-surface truthfulness: the docs-root, checklist, tests-root, and packet-local notes must keep the recovered documentation packet visible without presenting the current Makefile as if it still reruns `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` inside `phase14-validate`
  * the broader repo-reality gap is now the unrecovered build, manifest, survey, and bridge layer listed above, so this note must not present those paths as freshly re-read executable evidence in this lane until they return through the same exact readback mode
  * the attached-toolchain boundary still belongs here, but only as a truthfulness guard: while `zigux/Makefile` lacks `phase14-*` targets, this note should not offer wrapper-backed attached-toolchain reruns as if they are currently executable in the recovered packet
  * the current scripts-root reminder mirrors the same Phase 14 route split and keeps the missing `phase14-*` wrappers framed as packet-local or repo-reality-gap vocabulary, so this shared note should stay aligned with that current scripts-root posture instead of preserving stale wrapper-backed examples
  * all four anchor families remain parked on study-only or freeze-in-C posture, so no anchor-local reopen is justified from this shared note alone

## Productization evidence
  * named owner: `Core-Adjacent Pod`
  * status bucket: `study_only`
  * evidence mode: `documentation_layer_recovered_mixed_source_reminder_layer_plus_workqueue_boundary_shard_partial_executable_layer`
  * rollback owner: `Repo Tooling Pod`
  * rollback threshold: `0` tolerated same-packet drifts across the recovered documentation packet, the blob-readable validator path, the readable current Makefile body, the directly readable workqueue boundary shard, and the still-missing executable packet members
  * fallback path: keep this shared smoke lane aligned with the current gap notes until the broader shared reminder packet stops treating the current Makefile body as if it still shipped the older `phase14-*` routes, and until the missing executable packet members above return through exact current-`master` contents readback; once they do, rerun the packet-local commands below before restoring any stronger validator-first claim
  * automatic return-to-blocked triggers:
    * recovered documentation packet drift
    * validator-versus-reminder-surface drift
    * workqueue-boundary-shard drift
    * executable packet member drift
    * anchor-local reminder drift
    * attached-toolchain guidance drift inside the shared smoke note
  * ZAR-to-product transfer rationale: absorb ZAR runtime research as product discipline only by keeping exported evidence notes, exact readback truthfulness, explicit blocker posture, bounded rerun guidance, and directly readable anchor-local boundary shards visible without turning partial readback into a parity or ownership claim

## Non-goals

This shared smoke slice does not claim:

  * live workqueue execution, draining, or cancellation parity
  * skbuff lifetime, destructor, checksum, or segmentation ownership
  * `kernel/trace/ring_buffer.zig`
  * `kernel/rcu/tree_bridge.zig`
  * any new focused replay route for the four anchor-local packets
  * any direct current-`master` build-backed proof beyond the recovered documentation layer, the blob-readable validator path, the readable Makefile body with its shipped non-Phase-14 routes, the directly readable workqueue boundary shard, and the still-partial executable packet
  * any Phase 14 status change beyond keeping the current evidence packet truthful

## Packet-Local Rerun Vocabulary

This lane no longer treats the older `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase14`, or their `ZIG=/absolute/path/to/attached-zig/zig ...` variants as current rerun guidance, because the readable `zigux/Makefile` body still does not materialize those targets on current `master`.

Keep those wrapper names only as historical packet vocabulary until the same exact readback mode restores both the missing build-side files named above and the `phase14-*` Makefile routes. Until then, this note should record the limitation instead of suggesting an attached-toolchain wrapper fallback that the current packet cannot actually execute.

## Next bounded step

Keep this core-adjacent lane focused on shared reminder truthfulness and the shared smoke gap notes until the remaining executable packet members return.

If a future same-lane reread still finds `zigux/Makefile` readable while its live body still lacks `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` even though the returned file already exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes, publish the smallest broader reminder-surface repair that removes stale `phase14-*` Makefile-backed proof claims before reopening any validator-local handoff.

If a future same-lane reread keeps the directly readable workqueue boundary shard intact while the broader executable layer remains partial, keep this note, `Documentation/zigux/phase14-core-boundary-traceability.md`, and the surviving shared reminder packet aligned so the workqueue foothold stays explicit without overstating build-backed Phase 14 proof.

If a future same-lane reread restores current direct readback for `phase14-validate`, `phase14-smoke`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, or `zigux/tests/phase14_end_to_end_smoke_survey.zig`, reconcile this note with those files and with `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md` before restoring any stronger validator-first wording.

If the docs-root, checklist, or tests-root reminder surfaces are edited first, keep them aligned with the recovered documentation packet, the blob-readable validator path, the readable Makefile body with its shipped non-Phase-14 routes, the directly readable workqueue boundary shard, and the still-partial executable layer instead of implying a broader current-`master` replay.

## Footer