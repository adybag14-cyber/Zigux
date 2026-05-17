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
  * refreshed against fresh exact current-`master` contents recovery on `2026-05-17`
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
    * `scripts/zigux/validate-phase14.py`
  * executable packet members still unrecovered through this lane's exact contents path:
    * `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
    * `zigux/tests/phase14_build.zig`
    * `zigux/tests/phase14_end_to_end_smoke_manifest.json`
    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`
    * `zigux/tests/phase14_workqueue_bridge.zig`
    * `zigux/tests/phase14_skbuff_bridge.zig`
    * `zigux/tests/phase14_ring_buffer_survey.zig`
    * `zigux/tests/phase14_rcu_tree_survey.zig`
    * `net/core/skbuff_bridge.zig`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 still needs a small shared smoke packet that keeps those four anchors reviewable as one bounded evidence bundle instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It records the directly readable shared-smoke documentation layer, keeps the attached-toolchain fallback visible for the bounded rerun routes already named here, and makes the remaining executable-layer readback gap explicit instead of overstating repo reality.

## Exact evidence captured
  * directly readable current-`master` documentation layer:
    * the shared smoke survey, release-boundary survey, cross-anchor traceability note, productization-gap note, attached-toolchain guidance gap note, shared-smoke gap note, freeze map, docs-root summary, review checklist, skbuff survey, and Phase 15 study-only accounting companion are all directly readable again through this lane's contents path
  * directly readable executable-layer placeholder:
    * `scripts/zigux/validate-phase14.py` is directly readable again through this lane's contents path, but the current file body is only the placeholder text `probe`, so it does not yet restore validator-first proof or rerun coverage for the broader shared smoke packet
  * packet-local rerun vocabulary preserved by this note:
    * `make -C zigux phase14-validate`
    * `make -C zigux phase14-test`
    * `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
    * `make -C zigux phase14`
    * `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
    * `make -C zigux phase14-smoke`
  * attached-toolchain fallback examples for this note's bounded smoke routes:
    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`
  * current anchor posture reflected by the recovered documentation packet:
    * workqueue remains `Study / Boundary Only`
    * skbuff remains `Freeze In C Initially` and parked on `phase14-skbuff-live-ownership-blocker`
    * ring buffer remains `Study / Boundary Only`
    * RCU tree remains `Freeze In C Initially`

## Shared smoke findings
  * directly readable current-`master` evidence is no longer a docs-level absence of the shared smoke packet; the documentation layer is recoverable again through this lane's exact contents path
  * `scripts/zigux/validate-phase14.py` is also directly readable again, but only as the placeholder body `probe`, so this note must not treat that returned path as restored validator-first proof
  * the remaining repo-reality gap is the still-unrecovered release-boundary checker, build, manifest, survey, and bridge layer listed above, so this note must not present those paths as freshly re-read executable evidence in this lane until they return through the same exact readback mode
  * the attached-toolchain fallback still belongs here because it keeps the bounded rerun route explicit even while the executable packet is only partially recoverable; keeping that fallback visible is an operational aid, not a new delivery claim
  * the current scripts-root reminder does not provide a directly readable Phase 14 guidance block in this lane's contents path, so the attached-toolchain fallback remains packet-local guidance here rather than shared scripts-root guidance
  * all four anchor families remain parked on study-only or freeze-in-C posture, so no anchor-local reopen is justified from this shared note alone

## Productization evidence
  * named owner: `Core-Adjacent Pod`
  * status bucket: `study_only`
  * evidence mode: `documentation_layer_recovered_executable_layer_partial`
  * rollback owner: `Repo Tooling Pod`
  * rollback threshold: `0` tolerated same-packet drifts across the recovered documentation packet, the returned placeholder validator path, and the still-missing executable packet members
  * fallback path: keep this shared smoke lane aligned with the current gap notes until the missing executable packet members above return through exact current-`master` contents readback and the validator path grows beyond the current placeholder; once they do, rerun the packet-local commands below before restoring any stronger validator-first claim
  * automatic return-to-blocked triggers:
    * recovered documentation packet drift
    * placeholder validator-path drift
    * executable packet member drift
    * anchor-local reminder drift
    * attached-toolchain guidance drift inside the shared smoke note
  * ZAR-to-product transfer rationale: absorb ZAR runtime research as product discipline only by keeping exported evidence notes, exact readback truthfulness, explicit blocker posture, and bounded rerun guidance visible without turning partial readback into a parity or ownership claim

## Non-goals

This shared smoke slice does not claim:

  * live workqueue execution, draining, or cancellation parity
  * skbuff lifetime, destructor, checksum, or segmentation ownership
  * `kernel/trace/ring_buffer.zig`
  * `kernel/rcu/tree_bridge.zig`
  * any new focused replay route for the four anchor-local packets
  * any direct current-`master` validator-first or build-backed proof beyond the recovered documentation layer and the returned placeholder validator path
  * any Phase 14 status change beyond keeping the current evidence packet truthful

## Packet-Local Rerun Vocabulary

These commands remain the bounded rerun routes named by this packet, but this lane does not treat them as freshly re-read executable evidence again until the missing release-boundary checker and build files above return through the same exact contents path and the validator file is more than the current placeholder.

1. rerun the shared packet when the validator and build layer is directly readable again

  * `make -C zigux phase14-validate`
  * `make -C zigux phase14-test`
  * `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  * `make -C zigux phase14`

2. rerun the focused smoke shard when the dedicated build file is directly readable again

  * `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  * `make -C zigux phase14-smoke`

3. rerun the same bounded packet with the attached toolchain when `zig` is unavailable on `PATH`

  * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
  * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
  * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`

## Next bounded step

Keep this core-adjacent lane parked unless the shared smoke note, the Phase 14 gap notes, or the exact contents readback set changes.

If a future same-lane reread recovers `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, or `zigux/tests/phase14_end_to_end_smoke_survey.zig`, reconcile this note with those files and with `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md` before restoring any stronger validator-first wording.

If the validator path stops being the placeholder `probe`, reconcile this note and `Documentation/zigux/phase14-shared-smoke-current-master-gap.md` before treating the file as restored validator-first evidence.

If the docs-root, checklist, or tests-root reminder surfaces are edited first, keep them aligned with the recovered documentation packet, the returned placeholder validator path, and the still-partial executable layer instead of implying a broader current-`master` replay.

## Footer