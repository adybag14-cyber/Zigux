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

Current `master` still carries the four-anchor Phase 5 reminder packet together with its shared contributor surfaces, but the directly readable sample-local evidence is now mixed rather than evenly restored across every anchor.

- shared reminder surfaces:
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
- directly readable bytestream packet:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `samples/zigux/bytestream_fifo.zig`
- directly readable kobject packet:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
- directly readable kretprobe packet:
  - `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  - `samples/zigux/kretprobe_example.zig`
  - `zigux/tests/phase5_kretprobe_example.zig`
  - `zigux/tests/phase5_kretprobe_example_manifest.json`
- directly readable trace-events packet:
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample_manifest.json`
  - `zigux/tests/phase5_trace_events_sample_survey.zig`

Fresh shared-surface readback also keeps these current gaps explicit:

- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`
- `zigux/tests/phase5_kobject_example_survey.zig`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

Some shared reminder surfaces still narrate the older kretprobe-gap posture. Do not route shared sequencing work as though kretprobe still sits inside a survey-note-only gap, and do not route bytestream or kobject work as though the older tests-root or shared-build companions are directly readable again just because those narrower packets are still reviewable.

That means current Phase 5 work is no longer about adding a missing anchor. The live overlap risk is now two-sided:

- shared reminder-surface edits can still reopen bytestream, kobject, kretprobe, or trace-events packet work when a note accidentally reclassifies those packet shapes
- stale owner-map wording can still send kretprobe back into missing-path follow-through even though its current public evidence now includes a restored sample-root-plus-tests packet

## Owner map

### Shared sample-lane owner

Treat this sequencing note together with `Documentation/zigux/phase5-sample-review-guide.md` as the shared owner map for reminder-surface work that spans more than one Phase 5 sample.

That shared lane owns only:

- the shared contributor packet in `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- wording that keeps the roadmap-backed four-anchor packet explicit while also keeping the current direct-readback split explicit
- wording that keeps bytestream routed through its survey-note-plus-sample packet, kobject routed through its note-plus-sample-plus-tests packet, kretprobe routed through its restored note-plus-sample-plus-tests packet, and trace-events routed through its directly readable non-runtime packet
- wording that keeps the current missing shared `zigux/tests/phase5_build.zig` route explicit instead of presenting a live Linux-style shared replay path on current `master`
- wording that keeps the Phase 5 versus Phase 9 boundary explicit for the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families
- no-extra-sample reminders for helper families such as `string`, `cmdline`, `argv`, `rbtree`, direct `bitmap`, and standalone formatting samples

This shared lane does not own sample behavior, sample-local manifests, sample-local survey gates, packet-specific replay wording, or missing-path metadata updates inside one per-sample note unless the change is only restating an already landed shared boundary.

### Bytestream FIFO packet

The bytestream FIFO lane currently owns the directly readable landed packet for:

- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `samples/zigux/bytestream_fifo.zig`

Keep bytestream-local follow-through inside the approved fixed-buffer FIFO packet: `StorageBacking.embedded_fixed_buffer`, `previewInto()`, `snapshotInto()`, the exact `reviewContract().focus` order, helper-boundary cues, queue-shape cues, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path.

Do not reopen the older bytestream tests-root or shared-build companions from this lane until a fresh reread proves those exact paths returned.

### Kobject packet

The kobject lane currently owns the directly readable landed packet for:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`

Keep kobject-local follow-through inside the approved ownership-and-lifetime packet: `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, `runTeardownReplay()`, `ownershipSummary()`, and the `abandoned_before_registration` versus `tore_down_registered_attributes` split.

Do not reopen `zigux/tests/phase5_kobject_example_survey.zig` or the older shared-build path from this lane until a fresh reread proves those exact paths returned.

### Kretprobe packet

The kretprobe lane currently owns the restored directly readable non-runtime packet for:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`

Keep kretprobe-local follow-through inside that restored packet: `runRetargetReplay()`, `runAnchorReplay()`, `runLifecycleGuardReplay()`, `runOwnershipReplay()`, `runRecoveryReplay()`, the explicit `kernel_clone` default symbol, the direct `do_sys_openat2` retarget cue, the bounded `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and `maxactive = 20` replay contract, and the `cold` through `exited` ownership snapshots.

Do not restate the missing `zigux/tests/phase5_kretprobe_example_survey.zig` or shared `zigux/tests/phase5_build.zig` route as directly readable evidence from this lane until a fresh reread proves those exact paths returned.

### Trace-events packet

The trace-events lane currently owns the directly readable non-runtime packet for:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Keep trace-events-local follow-through inside that directly readable packet: `formattedMessage()`, `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, `runLifecycleBoundaryReplay()`, the exact `checked_focus` order, the selected-string plus `iter=%d` formatting cue, the public lifecycle summary, the callback-balance cues, and the post-`exit()` replay rejection boundary.

Do not restate the missing shared `zigux/tests/phase5_build.zig` route as directly readable evidence from this lane until a fresh reread proves that exact path returned.

## Anti-overlap rules

When a Phase 5 change is proposed, choose the narrowest owner first.

- If a change only repairs one sample survey note, one sample file, one focused replay, one manifest, or one survey gate, keep it inside that single sample packet.
- If a change only refreshes how the four approved anchors, the current direct-readback split, or the Phase 5 versus Phase 9 boundary are described together, keep it in the shared reminder packet.
- If one shared reminder surface still treats kretprobe as survey-note-only even though the restored packet is directly readable on current `master`, keep the repair to one shared-surface owner-map correction instead of reopening sample-local kretprobe behavior work.
- If bytestream, kobject, kretprobe, or trace-events still expose directly readable packet evidence, point shared docs at those exact packet-local surfaces instead of flattening them into one stale gap posture.
- Do not use the shared sample lane to move packet-local `PHASE5_LANE_KEY`, `PHASE5_SURVEYED_COMMIT`, manifest markers, or focused replay expectations.
- Do not use a sample-local lane to rewrite shared no-extra-sample boundaries for `string`, `cmdline`, `argv`, `rbtree`, direct `bitmap`, or standalone formatting samples.
- Do not count `samples/zigux/runtime_*.zig` or `*_loader.zig` follow-ons as extra Phase 5 evidence; keep those under the separate Phase 9 runtime owner map.

## Next-step filter

Use this note to keep future Phase 5 follow-through bounded:

- reopen the shared sample lane only for one reminder-surface or owner-map truthfulness repair across the current four-anchor packet and its direct-readback split
- reopen the bytestream lane only for one packet-local sample-surface or directly coupled survey-note repair inside the still-readable survey-note-plus-sample packet
- reopen the kobject lane only for one packet-local manifest, sample-surface, or replay-contract repair inside the still-readable note-plus-sample-plus-tests packet
- reopen the kretprobe lane only for one packet-local manifest, sample-surface, or replay-contract repair inside the restored note-plus-sample-plus-tests packet
- reopen the trace-events lane only for one packet-local manifest, survey, replay-contract, or sample-surface repair inside the directly readable non-runtime packet
- update the directly coupled sample packet first when sample behavior changes, then refresh shared reminder surfaces only after those packet-local paths are directly readable on current `master`

This keeps Phase 5 aligned with the roadmap's delivered sample set while preventing shared note maintenance from turning back into overlapping sample work.