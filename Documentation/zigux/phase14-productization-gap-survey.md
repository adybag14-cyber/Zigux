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

The attached ZAR runtime archive reinforces the same product boundary.
Its value for this lane is smoke-check structure, blocked-state accounting, and rollback-minded validation discipline, not permission to present runtime experiments as current Zigux ownership, parity, or bridge-delivery evidence.

## Current Direct-Readback Evidence

Fresh GitHub contents reads on 2026-05-25 keep a broader and more precise Phase 14 documentation packet on current `master` than this note recorded on 2026-05-22, and the current lane can also recover a broader set of adjacent non-doc surfaces through current contents reads.

The current directly readable or recoverable Phase 14 summary and companion surfaces are:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase14-productization-gap-survey.md`
- `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`
- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-core-boundary-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase14-compile-shard-matrix-survey.md`
- `Documentation/zigux/phase14-workqueue-bridge-survey.md`
- `Documentation/zigux/phase14-ring-buffer-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- `Documentation/zigux/phase14-rcu-tree-survey.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `zigux/Makefile` through the current contents path
- `scripts/zigux/check-phase14-shared-smoke-route.py` through the current contents path
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` through the current contents path
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` through the current contents path
- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` through the current contents path
- `scripts/zigux/check-phase14-skbuff-compile-route.py` through the current contents path
- `scripts/zigux/check-phase14-ring-buffer-compile-route.py` through the current contents path
- `scripts/zigux/check-phase14-rcu-compile-route.py` through the current contents path
- `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` through the current contents path
- `scripts/zigux/validate-phase14.py` through the current contents path
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` through the current contents path
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path
- `kernel/workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_reviewability.zig`
- `zigux/tests/phase14_workqueue_bridge_manifest.json`
- `zigux/tests/phase14_ring_buffer_survey.zig`

That means the current productization gap is no longer a docs-level absence of the shared smoke packet.
Current `master` does expose the shared smoke note, the cross-anchor traceability note, the release-boundary note, the compile-shard matrix survey, the workqueue-local survey, the ring-buffer-local survey, the freeze map, the shared gap notes, the returned shared smoke manifest, the returned rollback-threshold, dedicated skbuff stay-in-C, dedicated skbuff compile-route, dedicated ring-buffer compile-route, dedicated RCU compile-route, dedicated RCU rollback guards, and the returned ring-buffer survey companion through the exact or mixed readback modes available in this lane.

It also now matters that the non-doc companion layers split in different ways:

- `zigux/Makefile` is readable again on current `master`, and its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate`, but no `phase14-smoke`, `phase14-test`, or `phase14` targets
- `scripts/zigux/check-phase14-shared-smoke-route.py` now returns through the current contents path and keeps the returned `phase14-validate` Makefile route plus workflow gate explicit instead of leaving that route proof only in neighboring reminder prose
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now returns through the current contents path and keeps the tests-root reminder aligned with the same recovered study-only split without promoting the broader `phase14-smoke`, `phase14-test`, or `phase14` wrappers
- the checker itself is directly readable again, and the current tests-root reminder now keeps `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, and `zigux/tests/phase14_ring_buffer_survey.zig` explicit inside the Phase 14 shared smoke packet, so the recovered note family no longer depends on an undercounted tests-root summary
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` now returns through the current contents path and keeps the shared rollback threshold, fallback path, automatic return-to-blocked triggers, and narrowed study-only route split explicit instead of leaving that rollback contract only in neighboring reminder prose
- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` now returns through the current contents path and keeps the dedicated `net/core/skbuff.c` freeze-in-C stay-in-C guard explicit beside the shared packet, so the current productization note should count that returned guard surface instead of leaving the skbuff ownership boundary implicit inside broader reminder prose
- `scripts/zigux/check-phase14-skbuff-compile-route.py` now returns through the current contents path and keeps the dedicated `net/core/skbuff.c` compile-shard route explicit beside the shared packet, the shared smoke manifest, and the current validator route, so the current productization note should count that returned guard surface instead of leaving skbuff compile evidence implicit inside broader reminder prose
- `scripts/zigux/check-phase14-ring-buffer-compile-route.py` now returns through the current contents path and keeps the dedicated `kernel/trace/ring_buffer.c` compile-shard row explicit beside the shared packet, the shared smoke manifest, and the current validator route, so the current productization note should count that returned guard surface instead of leaving ring-buffer compile evidence implicit inside broader reminder prose
- `scripts/zigux/check-phase14-rcu-compile-route.py` now returns through the current contents path and keeps the dedicated `kernel/rcu/tree.c` compile-shard row explicit beside the shared packet, the shared smoke manifest, and the current validator route, so the current productization note should count that returned guard surface instead of leaving the RCU compile-route posture implicit inside broader reminder prose
- `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` now returns through the current contents path and keeps the dedicated `kernel/rcu/tree.c` freeze-in-C rollback guard explicit beside the shared packet, so the current productization note should count that returned guard surface instead of leaving the RCU rollback posture implicit inside the broader validator
- `scripts/zigux/validate-phase14.py` now returns through the current contents path and carries a real shared-smoke validator surface rather than the older placeholder-only body
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the recovered shared reminder packet
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now returns through the current contents path and keeps the machine-readable shared smoke surface inventory plus the narrowed single-gate compile-shard posture explicit beside the returned `phase14-validate` route instead of leaving the manifest in the exact-readback-gap bucket; the same live body now records both the returned skbuff compile-route checker, the returned ring-buffer compile-route checker, and the returned RCU compile-route checker as validator-backed packet members
- `Documentation/zigux/phase14-compile-shard-matrix-survey.md` now returns through the current contents path and keeps the exact `6 / 1 / 5` compile-shard split explicit beside the shared gate, the focused build-file shard, and the dedicated skbuff, ring-buffer, and RCU route guards, so the productization note should count that returned matrix surface instead of leaving compile-route posture spread only across reminder prose and the manifest
- `Documentation/zigux/phase14-workqueue-bridge-survey.md` now returns through the current contents path and keeps the review-only workqueue study packet, the blocked live-execution boundary, and the direct `zig test zigux/tests/phase14_workqueue_reviewability.zig` trust gate explicit beside the shared packet, so the productization note should keep that anchor-local study surface visible instead of collapsing it into generic shared-smoke wording
- `Documentation/zigux/phase14-ring-buffer-survey.md` now returns through the current contents path and keeps the ring-buffer-local boundary decision checklist, maintenance-mode handoff, and returned survey companion posture explicit beside the shared packet, so the productization note should keep that anchor-local study surface visible instead of leaving ring-buffer runtime-research absorption implied through the broader shared reminder family alone
- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard, so this productization note should keep that study-only foothold explicit instead of leaving part of it in the missing executable layer
- `zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion, so this productization note should keep that returned study-only foothold explicit instead of leaving it inside the exact-readback gap bucket
- `Documentation/zigux/phase14-rcu-tree-survey.md` is directly readable again through the current contents path while its executable companions remain public-fallback-backed, so the shared productization packet should keep that returned freeze-in-C companion explicit without turning the still-partial RCU executable layer into a direct replay claim

## Current Readback Gaps

Direct GitHub contents reads in this lane still return missing-path results for these executable Phase 14 packet members:

- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `net/core/skbuff_bridge.zig`

This means the current productization gap is narrower and more specific than the older note claimed.
The remaining drift is the split between the directly readable shared-smoke documentation surfaces, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable rollback-threshold sequencing checker, the directly readable dedicated skbuff stay-in-C guard, the directly readable dedicated skbuff compile-route guard, the directly readable dedicated ring-buffer compile-route guard, the directly readable dedicated RCU compile-route guard, the directly readable dedicated RCU rollback guard, the directly readable validator body, the directly readable release-boundary exact-count guard, the directly readable compile-shard matrix survey, the directly readable shared smoke manifest, the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets, the directly readable workqueue reviewability shard, the directly readable workqueue survey note, the directly readable ring-buffer survey note, the directly readable ring-buffer survey companion, the directly readable RCU survey note, and the still-unrecovered executable survey, build, and skbuff-side bridge layer beneath them.

The active same-lane gap is therefore now the exact-readback executable-layer misses above.

The shared reminder family is now aligned around the directly readable shared-smoke documentation surfaces, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable rollback-threshold sequencing checker, the directly readable dedicated skbuff stay-in-C guard, the directly readable dedicated skbuff compile-route guard, the directly readable dedicated ring-buffer compile-route guard, the directly readable dedicated RCU compile-route guard, the directly readable dedicated RCU rollback guard, the directly readable validator body, the directly readable release-boundary exact-count guard, the directly readable compile-shard matrix survey, the directly readable shared smoke manifest, the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets, the directly readable workqueue reviewability shard, the directly readable workqueue survey note, the directly readable ring-buffer survey note, the directly readable ring-buffer survey companion, and the directly readable RCU survey note.

## Product Judgment

Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.

Given current repo readback, the next honest delivery move is no longer the older validator-local exact-line handoff.
The higher-value same-lane task is reminder-surface truthfulness: keep shared notes aligned with the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable rollback-threshold sequencing checker, the directly readable dedicated skbuff stay-in-C guard, the directly readable dedicated skbuff compile-route guard, the directly readable dedicated ring-buffer compile-route guard, the directly readable dedicated RCU compile-route guard, the directly readable dedicated RCU rollback guard, the directly readable validator surface, the directly readable release-boundary exact-count guard, the directly readable compile-shard matrix survey, the directly readable shared smoke manifest, the directly readable workqueue reviewability shard, the directly readable workqueue survey note, the directly readable ring-buffer survey note, the directly readable ring-buffer survey companion, the directly readable RCU survey note, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships the old `phase14-*` routes.

That is also the right absorption boundary for ZAR runtime research in this lane: keep any imported value limited to smoke sequencing, blocked-state vocabulary, rollback thresholds, and reviewability discipline. Do not let runtime research artifacts collapse the distinction between returned study notes and still-missing executable packet members, and do not let them reopen workqueue, ring buffer, skbuff, or RCU ownership claims ahead of the roadmap.

Right now the smallest previously open reminder drift has been closed: this productization note now keeps the returned compile-shard matrix survey, the returned workqueue survey, the returned ring-buffer survey, the returned RCU compile-route checker, and the returned runtime-research absorption boundary explicit beside the already-recovered shared smoke packet members.

Reviewers should therefore treat the shared smoke documentation packet as directly readable current evidence again, treat `scripts/zigux/check-phase14-shared-smoke-route.py` as directly readable current route evidence, treat `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` as directly readable current tests-surface evidence, treat `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` as directly readable current rollback-threshold evidence, treat `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` as directly readable current freeze-in-C stay-in-C evidence for the skbuff anchor, treat `scripts/zigux/check-phase14-skbuff-compile-route.py` as directly readable current skbuff compile-route evidence, treat `scripts/zigux/check-phase14-ring-buffer-compile-route.py` as directly readable current ring-buffer compile-route evidence, treat `scripts/zigux/check-phase14-rcu-compile-route.py` as directly readable current RCU compile-route evidence, treat `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` as directly readable current freeze-in-C rollback evidence for the RCU anchor, treat `scripts/zigux/validate-phase14.py` as directly readable current evidence rather than a blob-readable mixed-source file, keep `scripts/zigux/check-phase14-release-boundary-exact-counts.py` explicit as directly readable release-facing evidence, keep `Documentation/zigux/phase14-compile-shard-matrix-survey.md` explicit as directly readable current compile-matrix evidence, keep `zigux/tests/phase14_end_to_end_smoke_manifest.json` explicit as directly readable machine-readable shared-smoke evidence, keep the workqueue-local reviewability shard explicit as returned study-only evidence, keep `Documentation/zigux/phase14-workqueue-bridge-survey.md` explicit as returned study-only workqueue packet evidence, keep `Documentation/zigux/phase14-ring-buffer-survey.md` explicit as returned study-only ring-buffer packet evidence, keep the ring-buffer survey companion explicit as returned study-only evidence, keep `Documentation/zigux/phase14-rcu-tree-survey.md` explicit as a returned dedicated freeze-in-C companion note, and still treat the executable build, focused survey, and skbuff bridge companions above as repo-reality gaps until they return through the same exact contents path.

## Recommended Next Bounded Step

Stay in the same core-adjacent lane and keep the surviving shared reminder packet aligned around this 2026-05-25 readback split.

The next honest follow-up is now whichever smaller shared reminder surface or executable-layer readback boundary next drifts against that recovered packet. If a neighboring same-family reminder lane reopens `zigux/tests/README.md` or another shared note, it should preserve `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-compile-shard-matrix-survey.md`, `Documentation/zigux/phase14-workqueue-bridge-survey.md`, `Documentation/zigux/phase14-ring-buffer-survey.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`, `scripts/zigux/check-phase14-skbuff-compile-route.py`, `scripts/zigux/check-phase14-ring-buffer-compile-route.py`, `scripts/zigux/check-phase14-rcu-compile-route.py`, and `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` beside the already-recovered shared smoke packet members without promoting the missing executable-layer paths or the absent `phase14-smoke`, `phase14-test`, and `phase14` wrappers.

Beyond that reminder-side undercount, re-evaluate the next smallest same-lane surface only if one of the current reminder notes stops keeping the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable rollback-threshold sequencing checker, the directly readable dedicated skbuff stay-in-C guard, the directly readable dedicated skbuff compile-route guard, the directly readable dedicated ring-buffer compile-route guard, the directly readable dedicated RCU compile-route guard, the directly readable dedicated RCU rollback guard, the directly readable validator surface, the directly readable release-boundary exact-count guard, the directly readable compile-shard matrix survey, the directly readable shared smoke manifest, the directly readable workqueue reviewability shard, the directly readable workqueue survey note, the directly readable ring-buffer survey note, the directly readable ring-buffer survey companion, the directly readable RCU survey note, and the readable non-owner Makefile posture with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` aligned, or if the missing executable packet members above return through exact current-`master` readback.