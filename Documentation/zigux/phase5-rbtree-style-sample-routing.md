# Phase 5 Rbtree-Style Sample Routing

This note keeps the mismatched Phase 5 `rbtree`-style sample wording honest against the current Zigux tree.

## Status

- `PHASE5_STATUS=routing-note`
- `PHASE5_LANE_KEY=P5-L20`
- scope: route the sample wording to the nearest live Phase 5 ownership-tree packet without inventing a fifth approved sample

## Current routing on `master`

The roadmap-backed Phase 5 sample anchors are still limited to:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Current `master` still ships no standalone `samples/zigux/*rbtree*` Phase 5 reference sample.

When the lane wording says `rbtree`-style sample work, route review through these bounded surfaces instead:

- `samples/zigux/kobject_example.zig` is the nearest live ownership-tree Phase 5 sample packet
- `zigux/tests/phase5_kobject_example.zig` is the directly coupled focused replay for that ownership-tree packet
- `Documentation/zigux/phase5-kobject-sample-survey.md` records the current kobject packet and its mixed direct-plus-public-tree-backed evidence
- `tools/lib/rbtree.zig` remains helper-owned Phase 1 evidence rather than Phase 5 sample-root proof
- `Documentation/zigux/phase5-sample-review-guide.md` and `samples/zigux/README.md` keep the no-extra-sample boundary explicit

## Boundary rules

Keep this lane narrow:

- do not describe `tools/lib/rbtree.zig` as a landed Phase 5 sample
- do not invent a fifth approved sample anchor under `samples/zigux/`
- do not widen this routing note into runtime-pilot, sysfs, procfs, or module-registration claims
- do not reopen helper semantics unless the helper-owned `tools/lib/rbtree.zig` packet itself changes

## Next bounded step

Leave this lane parked unless one of these moves together:

- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `samples/zigux/README.md`
- `tools/lib/rbtree.zig`

If one changes, reread the same ownership-tree and helper-boundary packet first and repair only the smallest same-lane routing drift.
