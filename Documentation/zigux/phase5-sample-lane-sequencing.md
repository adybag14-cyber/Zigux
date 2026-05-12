# Phase 5 Sample Lane Sequencing

This note records the current owner map for the shipped Phase 5 sample packet so shared reminder-surface work does not reopen the wrong sample lane.

## Scope

Use this note only for bounded sequencing and anti-overlap decisions across the shipped non-runtime Phase 5 sample packet.

Keep this note grounded in the roadmap-backed Phase 5 destination set:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the full Phase 5 sample set on current `master` unless the roadmap changes.

## Current repo reality

Current `master` already carries the full four-sample Phase 5 packet together with its shared contributor surfaces:

- shared reminder surfaces:
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
- sample-local packets:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `samples/zigux/bytestream_fifo.zig`
  - `samples/zigux/kobject_example.zig`
  - `samples/zigux/kretprobe_example.zig`
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_build.zig`
  - the four focused `zigux/tests/phase5_*` replay files, manifests, and survey gates paired with those samples

That means current Phase 5 work is no longer about adding a missing anchor. The live risk is overlap: shared reminder-surface edits reopening per-sample packet work, or per-sample truthfulness repairs drifting into the shared Phase 5 packet without a bounded reason.

## Owner map

### Shared sample-lane owner

Treat this sequencing note together with `Documentation/zigux/phase5-sample-review-guide.md` as the shared owner map for reminder-surface work that spans more than one Phase 5 sample.

That shared lane owns only:

- the shared contributor packet in `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- wording that keeps the shipped four-sample packet explicit
- wording that keeps `zig build test --build-file zigux/tests/phase5_build.zig --summary all` as the shared replay route while `make -C zigux phase5-test` and `make -C zigux phase5` stay local wrappers over that same build entrypoint
- wording that keeps the Phase 5 versus Phase 9 boundary explicit for the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families
- no-extra-sample reminders for helper families such as `string`, `cmdline`, `argv`, `rbtree`, direct `bitmap`, and standalone formatting samples

This shared lane does not own sample behavior, sample-local manifests, sample-local survey gates, or packet-specific replay wording unless the change is only restating an already landed shared boundary.

### Bytestream FIFO packet

The bytestream FIFO lane owns only the landed packet for:

- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `samples/zigux/bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`

Keep bytestream-local follow-through inside the approved fixed-buffer FIFO packet: `StorageBacking.embedded_fixed_buffer`, `previewInto()`, `snapshotInto()`, the exact `reviewContract().focus` order, helper-boundary cues, queue-shape cues, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path.

### Kobject packet

The kobject lane owns only the landed packet for:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

Keep kobject-local follow-through inside the approved ownership-and-lifetime packet: `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, `runTeardownReplay()`, `ownershipSummary()`, and the `abandoned_before_registration` versus `tore_down_registered_attributes` split.

### Kretprobe packet

The kretprobe lane owns only the landed packet for:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

Keep kretprobe-local follow-through inside the approved probe-lifecycle packet: `runRetargetReplay()`, `runRecoveryReplay()`, `runOwnershipReplay()`, `runLifecycleGuardReplay()`, the fixed `maxactiveBudget()` cue at `20`, timestamp-order rejection and recovery, the missed-instance summary, and post-exit handler rejection.

### Trace-events packet

The trace-events lane owns only the landed packet for:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Keep trace-events-local follow-through inside the approved payload, callback, and ownership packet: `formattedMessage()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `runOwnershipReplay()`, the exact `checked_focus` order, and the restored registration-balance plus post-exit rejection boundaries.

## Anti-overlap rules

When a Phase 5 change is proposed, choose the narrowest owner first.

- If a change only repairs one sample survey note, one sample file, one focused replay, one manifest, or one survey gate, keep it inside that single sample packet.
- If a change only refreshes how the four landed samples, the shared build route, or the Phase 5 versus Phase 9 boundary are described together, keep it in the shared reminder packet.
- If a shared reminder surface needs one sample-specific cue, point to that exact landed packet instead of restating behavior from memory.
- Do not use the shared sample lane to move packet-local `PHASE5_LANE_KEY`, `PHASE5_SURVEYED_COMMIT`, manifest markers, or focused replay expectations.
- Do not use a sample-local lane to rewrite shared no-extra-sample boundaries for `string`, `cmdline`, `argv`, `rbtree`, direct `bitmap`, or standalone formatting samples.
- Do not count `samples/zigux/runtime_*.zig` or `*_loader.zig` follow-ons as extra Phase 5 evidence; keep those under the separate Phase 9 runtime owner map.

## Next-step filter

Use this note to keep future Phase 5 follow-through bounded:

- reopen the shared sample lane only for one reminder-surface or owner-map truthfulness repair across the already landed four-sample packet
- reopen a sample-local lane only for one packet-local manifest, survey, replay-contract, or sample-surface repair
- update the directly coupled sample packet first when sample behavior changes, then refresh shared reminder surfaces only after those packet-local paths are directly readable on current `master`

This keeps Phase 5 aligned with the roadmap's delivered sample set while preventing shared note maintenance from turning back into overlapping sample work.