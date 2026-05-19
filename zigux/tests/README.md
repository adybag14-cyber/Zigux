# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

## Phase 14 shared smoke packet

Keep the current bounded Phase 14 reminder packet explicit through `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and keep the blob-readable `scripts/zigux/validate-phase14.py` plus the directly readable workqueue reviewability shard explicit as mixed-source evidence rather than missing executable-layer proof.

Keep the directly readable workqueue reviewability shard explicit through `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` so the tests-root reminder records the returned study-only foothold instead of leaving it inside the missing executable-layer bucket.

Keep `scripts/zigux/check-phase14-release-boundary-exact-counts.py` explicit as the directly readable release-boundary truthfulness guard beside the blob-readable validator surface and the returned workqueue shard.

Current `master` does materialize `zigux/Makefile`, but its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets, so keep the returned file framed as current repo evidence without promoting the older Phase 14 route names into shipped tests-root proof.

Keep the attached-toolchain fallback explicit as packet-local rerun vocabulary rather than current build-backed evidence:
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`

Keep the blob-readable `scripts/zigux/validate-phase14.py` explicit as the current mixed-source validator surface for this packet, and treat checker-local Phase 14 follow-through as separate review-path work until a fresh current-`master` readback returns it directly.

Current `master` still does not materialize `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, or `net/core/skbuff_bridge.zig`, so keep that executable-layer packet framed as a repo-reality gap rather than shipped tests-root evidence until fresh current-tree reads restore it.

Keep the four roadmap-owned anchors explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors, while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors unless a later Architecture Council packet records a status change.

Tests-root reviewer prompt:
- Does the bounded Phase 14 reminder keep the recovered documentation packet, the blob-readable validator surface, the directly readable release-boundary truthfulness guard, the directly readable workqueue reviewability shard, the attached-toolchain rerun vocabulary, the readable current `zigux/Makefile` surface that now exposes shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes while still omitting all `phase14-*` targets, and the still-missing executable-layer gaps aligned without reviving the older `phase14-*` Makefile routes as shipped current-`master` evidence?
