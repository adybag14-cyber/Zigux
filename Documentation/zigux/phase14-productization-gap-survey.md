# Phase 14 Productization Gap Survey

## Purpose

This note records the current Phase 14 repo-reality gap against the roadmap-backed study-only target.

The goal here is not to widen the Phase 14 surface.
The goal is to keep the current work reviewable, truthful, and bounded before any further bridge or smoke claims are repeated.

## Roadmap Baseline

Phase 14 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the `Core-Adjacent Bounded Internals` lane.

Roadmap expectations for this lane:

- boundary maps
- concurrency audits
- explicit stay-in-C decisions where warranted
- wrapper-first or study-only posture

Primary Linux anchors for the lane:

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- `net/core/skbuff.c`
- `kernel/rcu/tree.c`

The roadmap also keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the boundary-study-only set and keeps `kernel/rcu/tree.c` plus `net/core/skbuff.c` in the active freeze-in-C set.

## Current Direct-Readback Evidence

Fresh GitHub contents reads on 2026-05-18 now recover a broader Phase 14 documentation packet on current `master` than this note recorded on 2026-05-17, and the current lane can also recover four adjacent non-doc surfaces through mixed read modes.

The current directly readable or recoverable Phase 14 summary and companion surfaces are:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase14-productization-gap-survey.md`
- `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`
- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-core-boundary-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `zigux/Makefile` through the current contents path
- `scripts/zigux/validate-phase14.py` through pinned blob readback
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` through the current contents path
- `kernel/workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_reviewability.zig`
- `zigux/tests/phase14_workqueue_bridge_manifest.json`

That means the current productization gap is no longer a docs-level absence of the shared smoke packet.
Current `master` does expose the shared smoke note, the cross-anchor traceability note, the release-boundary note, the freeze map, and the shared gap notes through the exact contents path available in this lane.

It also now matters that the four non-doc companion layers split in different ways:

- `zigux/Makefile` is readable again on current `master`, and its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes, but no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets
- `scripts/zigux/validate-phase14.py` is still not returned by the same path-based contents bridge, but it is recoverable again through pinned blob readback and now carries a real shared-smoke validator surface rather than the older placeholder-only body
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the recovered shared reminder packet
- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard, so this productization note should keep that study-only foothold explicit instead of leaving part of it in the missing executable layer

## Current Readback Gaps

Direct GitHub contents reads in this lane still return missing-path results for these executable or machine-readable Phase 14 packet members:

- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_ring_buffer_survey.zig`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `net/core/skbuff_bridge.zig`

This means the current productization gap is narrower and more specific than the older note claimed.
The remaining drift is the split between the directly readable shared-smoke documentation surfaces, the blob-readable validator body, the directly readable release-boundary exact-count guard, the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes but no Phase 14 targets, the directly readable workqueue reviewability shard, and the still-unrecovered executable survey, manifest, and skbuff-side bridge layer beneath them.

## Product Judgment

Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.

Given current repo readback, the next honest delivery move is no longer the older validator-local exact-line handoff.
The higher-value same-lane task is reminder-surface truthfulness: keep shared notes aligned with the recovered documentation packet, the blob-readable validator surface, the directly readable release-boundary exact-count guard, the directly readable workqueue reviewability shard, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships the old `phase14-*` routes.

Reviewers should therefore treat the shared smoke documentation packet as directly readable current evidence again, treat `scripts/zigux/validate-phase14.py` as blob-readable mixed-source evidence rather than a missing file, keep `scripts/zigux/check-phase14-release-boundary-exact-counts.py` explicit as directly readable release-facing evidence, keep the workqueue-local reviewability shard explicit as returned study-only evidence, and still treat the executable build, manifest, survey, and skbuff bridge companions above as repo-reality gaps until they return through the same exact contents path.

## Recommended Next Bounded Step

Stay in the same core-adjacent lane and keep the surviving shared reminder packet aligned around this 2026-05-18 readback split.

The next honest follow-up is no longer another tests-root reminder rewrite unless a fresh reread finds drift there again. Instead, re-evaluate the smallest same-lane surface only if one of the current reminder notes stops keeping the recovered documentation packet, the blob-readable validator surface, the directly readable release-boundary exact-count guard, the directly readable workqueue reviewability shard, and the readable non-owner Makefile posture with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes but no Phase 14 targets aligned, or if the missing executable packet members above return through exact current-`master` readback.