# Phase 14 Bounded-Internal Lane Sequencing

This note turns the live Phase 14 evidence on `master` into one bounded anti-overlap map for core-adjacent internal lanes only.

## Status

- `PHASE14_STATUS=study_only`
- `PHASE14_SEQUENCE=bounded-internal-lane-anti-overlap`
- lane: `P14-Y06`
- scope: use the current workqueue, ring-buffer, skbuff, and RCU packets plus the shared Phase 14 smoke and docs surfaces to say which lane owns which already-landed evidence and which shared routes are coordination-only

## Why this note exists

The live repo already carries four distinct Phase 14 anchor-local packets:

- the workqueue boundary-map packet around `kernel/workqueue.c`
- the ring-buffer survey packet around `kernel/trace/ring_buffer.c`
- the skbuff boundary-map packet around `net/core/skbuff.c`
- the RCU tree survey packet around `kernel/rcu/tree.c`

Those packets now share validator wiring, smoke wiring, a shared full-bundle replay, and cross-anchor docs surfaces. That shared review path is useful, but without a dedicated owner map nearby scheduled runs can still reopen the wrong packet just because the shared smoke note, traceability note, or release-boundary note happens to mention adjacent lane state.

This note keeps the Phase 14 tranche honest by separating shared coordination surfaces from anchor-local ownership.

## Shared packet versus lane ownership

Shared Phase 14 coordination surface:

- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-core-boundary-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_build.zig`
- `zigux/Makefile`
- `make -C zigux phase14-validate`
- `make -C zigux phase14-smoke`
- `make -C zigux phase14-test`
- `make -C zigux phase14`

These shared routes prove that the current bounded Phase 14 packet still replays together. They do not transfer ownership of an anchor-local manifest, survey note, review-only bridge, blocked gap, or ready-next decision.

## Lane map

`P14-L01` workqueue lane owns the workqueue boundary-map packet:

- `kernel/workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge_manifest.json`
- `Documentation/zigux/phase14-workqueue-bridge-slice.md`
- `Documentation/zigux/phase14-workqueue-bridge-survey.md`

Shared smoke and release notes may summarize this packet, but they do not own delayed-work requeue governance, pending-bit handoff reviewability, hotplug follow-through, or any future stay-in-C wording that belongs to the workqueue packet itself.

`P14-L08` ring-buffer lane owns the study-only ring-buffer packet:

- `zigux/tests/phase14_ring_buffer_survey.zig`
- `zigux/tests/phase14_ring_buffer_manifest.json`
- `Documentation/zigux/phase14-ring-buffer-survey.md`
- `Documentation/zigux/freeze-map.md` only when the ring-buffer study-only boundary wording itself is what moved

Shared traceability, smoke, or release notes may echo the ring-buffer lane key, surveyed commit, blocked gap, or current parked posture, but they should not become the place where reader-page, remote-reader, mapped-reader, wakeup, or exported-page copy-path follow-through is selected or repaired.

`P14-L11` skbuff lane owns the review-only skbuff bridge packet:

- `net/core/skbuff_bridge.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_skbuff_bridge_manifest.json`
- `Documentation/zigux/phase14-skbuff-bridge-slice.md`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md`

Shared Phase 14 coordination surfaces may restate the current freeze-in-C posture, but they do not own checksum-state wording, segmentation-tail publication reviewability, qdisc-facing stay-in-C guardrails, or the blocked live-ownership boundary that belongs to the skbuff packet.

`P14-L16` RCU tree lane owns the blocked RCU survey packet:

- `zigux/tests/phase14_rcu_tree_survey.zig`
- `zigux/tests/phase14_rcu_tree_manifest.json`
- `Documentation/zigux/phase14-rcu-tree-survey.md`
- `Documentation/zigux/freeze-map.md` only when the explicit RCU freeze wording itself is what drifted

Shared smoke, traceability, and release notes may name the blocked bridge posture, but they do not own the callback-offload, idle-watch, public-wait, memory-ordering, hotplug-migration, or rollback-threshold evidence that the RCU lane records directly.

## Shared wording lane

Use the shared Phase 14 wording lane only when the coordination surfaces themselves drift:

- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-core-boundary-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_build.zig`
- `zigux/Makefile`

Do not use the shared wording lane to smuggle anchor-local bridge, survey, manifest, blocker, or next-step changes. If a wording fix depends on moving anchor-local behavior, split that work back into the owning anchor lane.

## Anti-overlap rules

- If a Phase 14 run changes `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, or the paired workqueue slice or survey note, that work belongs to `P14-L01`.
- If a Phase 14 run changes `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_ring_buffer_manifest.json`, or `Documentation/zigux/phase14-ring-buffer-survey.md`, that work belongs to `P14-L08`.
- If a Phase 14 run changes `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, or the paired skbuff slice or survey note, that work belongs to `P14-L11`.
- If a Phase 14 run changes `zigux/tests/phase14_rcu_tree_survey.zig`, `zigux/tests/phase14_rcu_tree_manifest.json`, or `Documentation/zigux/phase14-rcu-tree-survey.md`, that work belongs to `P14-L16`.
- If a Phase 14 run changes only the shared smoke, traceability, release-boundary, docs-root, tests-root, validator, or make-route coordination surfaces, that work belongs to the shared wording lane instead of any anchor-local packet.
- `Documentation/zigux/freeze-map.md` should only move inside a Phase 14 lane when one anchor's explicit study-only or freeze-in-C wording truly drifts; otherwise it remains a shared governance surface rather than a shortcut into anchor-local work.
- Shared replay or checker drift should reopen the smallest directly coupled shared wording step unless the break truly requires synchronized edits across more than one anchor-local packet.

## Recommended next-step order

1. shared wording lane only when the shared coordination surfaces drift
2. workqueue lane when the change is truly about the workqueue bridge packet
3. ring-buffer lane when the change is truly about survey-only ring-buffer boundary evidence
4. skbuff lane when the change is truly about the skbuff bridge packet
5. RCU lane when the change is truly about blocked RCU survey evidence

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the shared Phase 14 coordination surfaces and one of the four anchor-local packets again. Any deeper bridge, survey, manifest, or blocker work should return to the owning Phase 14 anchor lane instead of expanding this note.
