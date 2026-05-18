# Phase 5 Sample Lane Sequencing

This note keeps the roadmap-backed Phase 5 lane narrow on current `master`.

## Purpose

Use this shared note when a Phase 5 change touches approved sample anchors, shared contributor guidance, or the tracing and probe reminder surfaces.

Keep the lane sequencing honest:

- stay inside the four approved non-runtime Linux sample anchors
- prefer one reminder-surface repair at a time
- keep roadmap anchors distinct from current repo-readback proof
- keep later runtime-facing sample families in the separate Phase 9 lane

## Approved anchors

Phase 5 remains limited to these roadmap-backed sample anchors:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the full Phase 5 destination set unless the roadmap changes.

## Current shared packet on `master`

Fresh repo-first inspection in this run confirmed that current `master` still keeps the shared Phase 5 reminder packet reviewable through these directly readable surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

The same reread also confirmed that current `master` now keeps the restored direct bytestream packet, the restored direct kretprobe packet, and the bounded trace-events formatting companion visible from the sample root, while the kobject anchor remains a roadmap-backed target plus shared reminder or repo-reality-gap surface until a fresh reread proves its sample-root port returned directly on current `master`.

Keep this shared note truthful about that narrower current packet instead of repeating older missing-sample wording for bytestream or older broader direct-sample wording for kobject or trace-events.

## Current sample-root reality

Current `samples/zigux/README.md` says the sample root directly exposes:

- `samples/zigux/README.md`
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

So the current direct sample-root evidence for the roadmap-backed non-runtime Phase 5 lane is the restored bytestream port, the restored kretprobe port, and the bounded trace-events formatting companion.
Treat `samples/zigux/bytestream_fifo.zig` as the current direct sample-root proof for its approved anchor.
Treat `samples/zigux/kretprobe_example.zig` as the current direct sample-root proof for its approved anchor.
Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.
Keep the kobject anchor in shared-reminder or repo-reality-gap wording until a fresh reread proves `samples/zigux/kobject_example.zig` returned directly on current `master`.

## Tracing and probe packet

For the tracing and probe lane, keep follow-through aligned with these bounded reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those files should describe:

- the roadmap-backed `kretprobe` and `trace_events` anchors
- the current split between the restored direct kretprobe packet and the narrower trace-events formatting-companion packet
- the approved selected-string plus `iter=%d` formatting idiom cue
- the rule that Phase 9 runtime trace-events files are not extra Phase 5 sample proof
- the returned direct kretprobe packet through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`
- the current trace-events packet split: the bounded formatting companion stays directly readable through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder surfaces, while `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay in repo-reality-gap or shared-reminder wording until authenticated contents reread stops returning 404 for those paths; keep `zigux/tests/phase5_build.zig` framed only as shared companion evidence until authenticated contents reread returns that path directly on `master`

## Sequencing rules

When the lane reopens, sequence same-lane work in this order:

1. Fix one shared reminder-surface drift first when current packet surfaces disagree.
2. Prefer a shared tracing or probe reminder repair before any sample-local behavior change when the shared surfaces fall behind the already landed packet.
3. Keep wording truthful about what current `master` directly exposes, what currently depends on public raw or tree fallback, and what remains only roadmap-backed guidance.
4. Do not invent validator routes, make wrappers, or workflow coverage that the repo does not ship.
5. Leave the lane parked after one bounded repair unless fresh inspection shows another equally small same-lane drift.

## Phase boundaries

Keep the non-runtime Phase 5 boundary explicit:

- do not widen Phase 5 work into runtime-loader or runtime-pilot behavior
- keep `samples/zigux/runtime_*.zig` and `*_loader.zig` families in the separate Phase 9 lane
- do not widen toward freeze-in-C anchors such as `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- do not pull study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` into this lane

Keep the no-extra-sample helper-family boundaries explicit too:

- current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet
- there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion

## Next-step posture

The next honest Phase 5 step is another one-file reminder-surface repair that keeps the approved anchors explicit without overstating kobject direct sample-root visibility, flattening the narrower trace-events formatting packet, or overstating the shared `zigux/tests/phase5_build.zig` route as direct authenticated proof.
