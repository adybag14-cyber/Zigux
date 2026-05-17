# Phase 5 Sample Lane Sequencing

This note keeps the roadmap-backed Phase 5 lane narrow on current `master`.

## Purpose

Use this shared note when a Phase 5 change touches approved sample ports, shared contributor guidance, or `Documentation/zigux` material backed by concrete samples.

Keep the lane sequencing honest:

- stay inside the four approved non-runtime Linux sample anchors
- prefer one reminder-surface or one sample-local packet repair at a time
- keep direct authenticated readback distinct from current public-tree-backed companion evidence
- keep later runtime-facing sample families in the separate Phase 9 lane

## Approved anchors

Phase 5 remains limited to these roadmap-backed sample anchors:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the full Phase 5 destination set unless the roadmap changes.

## Current shared packet on `master`

Fresh repo-first inspection in this run confirmed that current `master` keeps the shared Phase 5 reminder packet reviewable through these surfaces:

- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`

Keep `scripts/zigux/README.md` outside this shared owner map for now.
Current `master` still ships no dedicated `validate-phase5.py`, no `check-phase5-*.py` checker packet, and no `phase5-validate` or `phase5` scripts-root route.

## Current sample-backed packet

The directly readable Phase 5 sample-root evidence on current `master` is still:

- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Keep follow-through aligned with the current per-anchor packet shape instead of flattening every anchor into the same restored or missing posture.

### bytestream_fifo

Keep the bytestream anchor aligned with:

- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `samples/zigux/bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`

Keep the remaining bytestream companions explicit as current public-tree-backed support material rather than direct authenticated-contents proof:

- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`
- `zigux/tests/phase5_build.zig`

### kobject_example

Keep the kobject anchor aligned with:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`

Keep these broader companions explicit as current public-tree-backed support material rather than direct authenticated-contents proof:

- `zigux/tests/phase5_kobject_example_survey.zig`
- `zigux/tests/phase5_build.zig`

### kretprobe_example

Keep the kretprobe anchor aligned with:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

Keep `zigux/tests/phase5_build.zig` explicit as current public-tree-backed companion evidence rather than direct authenticated-contents proof.

### trace_events_sample

Keep the trace-events anchor aligned with:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Keep `zigux/tests/phase5_build.zig` explicit as current public-tree-backed companion evidence rather than direct authenticated-contents proof.

## Sequencing rules

When the lane reopens, sequence same-lane work in this order:

1. Fix one shared reminder surface drift first when two or more current packet surfaces disagree.
2. Use one sample-local survey, manifest, or focused replay follow-up only when a landed sample contract actually moved.
3. Keep shared wording truthful about which routes were directly readable in the current inspection and which remain public-tree-backed support material.
4. Do not invent scripts-root proof, validator routes, make wrappers, or workflow coverage that current `master` does not ship.
5. Leave the lane parked after one bounded repair unless fresh inspection shows another equally small same-lane drift.

## Phase boundaries

Keep the non-runtime Phase 5 boundary explicit:

- do not widen Phase 5 work into runtime-loader or runtime-pilot behavior
- keep `samples/zigux/runtime_*.zig` and `*_loader.zig` families in the separate Phase 9 lane
- do not widen toward freeze-in-C anchors such as `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- do not pull study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` into this lane

Keep the no-extra-sample helper-family boundaries explicit too:

- there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`

Keep those helper families under their existing Phase 1, Phase 4, Phase 7, or Phase 9 owner packets instead of implying a fifth or sixth Phase 5 sample.

## Next-step posture

The current lane is already substantive and parked below new sample behavior.
If it reopens, prefer the next one-file reminder-surface repair or the next directly coupled sample-backed survey or manifest sync that current `master` actually shows, rather than broadening into new sample growth, scripts-root churn, runtime claims, or cross-phase helper drift.
