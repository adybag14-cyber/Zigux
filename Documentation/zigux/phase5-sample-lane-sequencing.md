# Phase 5 Sample Lane Sequencing

This note records the current owner map for the roadmap-backed Phase 5 sample packet so shared reminder-surface work does not reopen the wrong sample lane.

## Scope

Use this note only for bounded sequencing and anti-overlap decisions across the shipped non-runtime Phase 5 sample packet.

Keep this note grounded in the roadmap-backed Phase 5 destination set:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the full Phase 5 sample set on current `master` unless the roadmap changes.

## Current repo reality

Current `master` still carries the four-anchor Phase 5 reminder packet together with its shared contributor surfaces, but direct readback is no longer uniform across all four sample families.

- shared reminder surfaces:
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
- directly readable bytestream packet:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `samples/zigux/bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - `zigux/tests/phase5_bytestream_fifo_survey.zig`
  - `zigux/tests/phase5_build.zig`
- directly readable kobject packet:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`
  - `zigux/tests/phase5_build.zig`
- survey-note-only parked packets:
  - `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`

Current survey-note readback for kretprobe and trace-events now treats the older sample-root and focused tests-root packet as missing until a fresh reread proves those paths returned. Do not route shared sequencing work as though `samples/zigux/kretprobe_example.zig`, `samples/zigux/trace_events_sample.zig`, the `zigux/tests/phase5_kretprobe_example*` files, or the `zigux/tests/phase5_trace_events_sample*` files are directly readable again just because the bytestream and kobject packets still are.

That means current Phase 5 work is no longer about adding a missing anchor. The live overlap risk is now two-sided: shared reminder-surface edits can still reopen bytestream or kobject packet work, and stale owner-map wording can also send kretprobe or trace-events back into sample-root or tests-root follow-through even though their current public evidence is parked at the survey-note layer.

## Owner map

### Shared sample-lane owner

Treat this sequencing note together with `Documentation/zigux/phase5-sample-review-guide.md` as the shared owner map for reminder-surface work that spans more than one Phase 5 sample.

That shared lane owns only:

- the shared contributor packet in `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- wording that keeps the roadmap-backed four-anchor packet explicit while also keeping the current direct-readback split explicit
- wording that keeps `zig build test --build-file zigux/tests/phase5_build.zig --summary all` as the shared replay route only for the sample packets that are still directly readable through that build entrypoint
- wording that keeps the Phase 5 versus Phase 9 boundary explicit for the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families
- no-extra-sample reminders for helper families such as `string`, `cmdline`, `argv`, `rbtree`, direct `bitmap`, and standalone formatting samples

This shared lane does not own sample behavior, sample-local manifests, sample-local survey gates, packet-specific replay wording, or missing-path metadata updates inside one per-sample note unless the change is only restating an already landed shared boundary.

### Bytestream FIFO packet

The bytestream FIFO lane currently owns the directly readable landed packet for:

- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `samples/zigux/bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`
- `zigux/tests/phase5_build.zig` as the shared build route for this directly readable packet

Keep bytestream-local follow-through inside the approved fixed-buffer FIFO packet: `StorageBacking.embedded_fixed_buffer`, `previewInto()`, `snapshotInto()`, the exact `reviewContract().focus` order, helper-boundary cues, queue-shape cues, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path.

### Kobject packet

The kobject lane currently owns the directly readable landed packet for:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`
- `zigux/tests/phase5_build.zig` as the shared build route for this directly readable packet

Keep kobject-local follow-through inside the approved ownership-and-lifetime packet: `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, `runTeardownReplay()`, `ownershipSummary()`, and the `abandoned_before_registration` versus `tore_down_registered_attributes` split.

### Kretprobe packet

The kretprobe lane currently owns the survey-note-only parked packet for:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`

Keep kretprobe-local follow-through inside that survey-note-only gap packet until a fresh reread proves `samples/zigux/kretprobe_example.zig`, the coupled `zigux/tests/phase5_kretprobe_example*` surfaces, and any shared build-route evidence are directly readable again. While that gap remains open, the kretprobe lane should repair only:

- survey-note truthfulness about the current readback gap
- one shared reminder-surface reference that still treats the missing kretprobe sample-root or tests-root packet as directly readable evidence

### Trace-events packet

The trace-events lane currently owns the survey-note-only parked packet for:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`

Keep trace-events-local follow-through inside that survey-note-only gap packet until a fresh reread proves `samples/zigux/trace_events_sample.zig`, the coupled `zigux/tests/phase5_trace_events_sample*` surfaces, and any shared build-route evidence are directly readable again. While that gap remains open, the trace-events lane should repair only:

- survey-note truthfulness about the current readback gap
- one shared reminder-surface reference that still treats the missing trace-events sample-root or tests-root packet as directly readable evidence

## Anti-overlap rules

When a Phase 5 change is proposed, choose the narrowest owner first.

- If a change only repairs one sample survey note, one sample file, one focused replay, one manifest, or one survey gate, keep it inside that single sample packet.
- If a change only refreshes how the four approved anchors, the current direct-readback split, or the Phase 5 versus Phase 9 boundary are described together, keep it in the shared reminder packet.
- If kretprobe or trace-events still sit at a survey-note-only posture on current `master`, do not reopen missing sample-root or tests-root follow-through from this shared lane; keep the repair to one survey-note truthfulness update or one shared surface naming the current gap.
- If bytestream or kobject still expose directly readable sample-root and tests-root evidence, point shared docs at those exact packet-local surfaces instead of borrowing cues from the parked kretprobe or trace-events packet.
- Do not use the shared sample lane to move packet-local `PHASE5_LANE_KEY`, `PHASE5_SURVEYED_COMMIT`, manifest markers, or focused replay expectations.
- Do not use a sample-local lane to rewrite shared no-extra-sample boundaries for `string`, `cmdline`, `argv`, `rbtree`, direct `bitmap`, or standalone formatting samples.
- Do not count `samples/zigux/runtime_*.zig` or `*_loader.zig` follow-ons as extra Phase 5 evidence; keep those under the separate Phase 9 runtime owner map.

## Next-step filter

Use this note to keep future Phase 5 follow-through bounded:

- reopen the shared sample lane only for one reminder-surface or owner-map truthfulness repair across the current four-anchor packet and its direct-readback split
- reopen the bytestream or kobject lane only for one packet-local manifest, survey, replay-contract, sample-surface, or shared-build-route repair inside the still-directly-readable packet
- reopen the kretprobe or trace-events lane only to repair the survey-note gap wording or to switch back to a restored sample-root and tests-root packet after a fresh reread proves those paths returned
- update the directly coupled sample packet first when sample behavior changes, then refresh shared reminder surfaces only after those packet-local paths are directly readable on current `master`

This keeps Phase 5 aligned with the roadmap's delivered sample set while preventing shared note maintenance from turning back into overlapping sample work.