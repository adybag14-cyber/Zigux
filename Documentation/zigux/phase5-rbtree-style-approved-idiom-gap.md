# Phase 5 Rbtree-Style Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 sample lane truthful when shared reminder surfaces are tempted to treat helper-side tree reviewability as if it were a landed Phase 5 sample-root packet.

## Roadmap boundary

Phase 5 still stays limited to these four non-runtime Linux sample anchors:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

That roadmap set does not include a standalone `rbtree` sample anchor.

## Current repo reality on `master`

Fresh sample-root reread in this lane still shows no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`.

Current `master` instead keeps the non-runtime Phase 5 packet bounded to:

- the bytestream sample and queue-window companion
- the mixed `kobject` sample packet plus attr-group companion
- the `kretprobe` sample plus instance-budget and probe-spec companions
- the bounded trace-events formatting and callback-focus companions

Those landed Phase 5 reminder surfaces already say that no standalone `*rbtree*` sample exists here:

- `samples/zigux/README.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`

This note exists to make that boundary explicit in one place when the lane needs an exact reminder.

## What not to promote into Phase 5 proof

Do not treat helper-side tree work as if it were Phase 5 sample-root evidence.

In particular, do not describe these helper packets as a fifth Phase 5 sample family:

- `tools/lib/rbtree.zig`
- `lib/rbtree.zig`
- `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `zigux/tests/phase7_build.zig`

Those paths belong to helper-focused Phase 1 or Phase 7 evidence, not to the Phase 5 sample-root packet.

## Approved wording for shared reminder surfaces

When a shared Phase 5 reminder needs to mention the tree-shaped gap, keep the wording narrow:

- current `master` still ships no standalone `samples/zigux/*rbtree*` Phase 5 reference sample
- any `rbtree` reviewability evidence lives under the helper packets, not the Phase 5 sample root
- this absence should not be described as a missing fifth sample, a blocked sample port, or a hidden runtime-substrate dependency

The honest posture is simpler: the roadmap never approved a standalone Phase 5 `rbtree` sample anchor, and the current repo still reflects that boundary.

## Review boundary

Use this note only to keep the no-`rbtree`-sample boundary explicit inside the Phase 5 sample lane.

Do not use it as proof of:

- a landed Phase 5 `rbtree` sample
- a blocked Phase 5 `rbtree` port
- a missing runtime prerequisite for tree reviewability
- a reason to widen Phase 5 beyond its four approved anchors

Keep helper-side `rbtree` discussion parked with the Phase 1 or Phase 7 helper packets unless the roadmap changes.

## Next bounded step

Leave this note parked unless a shared Phase 5 reminder surface starts implying that current `master` ships a standalone `samples/zigux/*rbtree*` sample, or that helper-side `rbtree` evidence should count as a fifth approved Phase 5 sample family.