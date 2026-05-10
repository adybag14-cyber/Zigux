# Phase 5 Sample Review Guide

This guide keeps the shipped Phase 5 reference-sample packet reviewable as one bounded non-runtime contributor surface.

## Purpose

Use this guide when a change touches any Phase 5 sample, its paired survey note, or the shared reviewer packet around the four shipped reference samples.

The roadmap-backed goal for Phase 5 is still narrow:

* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact replay routes visible
* avoid widening non-runtime samples into runtime-substrate claims

## Current shipped Phase 5 packet

Current `master` carries exactly four shipped non-runtime Phase 5 reference samples:

* `samples/zigux/bytestream_fifo.zig` for `samples/kfifo/bytestream-example.c`
* `samples/zigux/kobject_example.zig` for `samples/kobject/kobject-example.c`
* `samples/zigux/kretprobe_example.zig` for `samples/kprobes/kretprobe_example.c`
* `samples/zigux/trace_events_sample.zig` for `samples/trace_events/trace-events-sample.c`

Keep the shared Phase 5 reviewer packet aligned across:

* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `zigux/tests/phase5_build.zig`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

## Shared replay route

The shared Phase 5 replay route is:

* `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

The local Linux-style wrappers are:

* `make -C zigux phase5-test`
* `make -C zigux phase5`

Keep `.github/workflows/zigux-bootstrap.yml` honest by naming only the direct `zig build test --build-file zigux/tests/phase5_build.zig --summary all` command as the shared CI replay. The two `make` targets are local wrappers over that same build entrypoint, not separate validation lanes.

## Sample-by-sample prompts

When a change touches the bytestream FIFO packet, keep these cues explicit across the sample, survey note, manifest, and shared replay route:

* `StorageBacking.embedded_fixed_buffer`
* the exact queue-order drain contract
* the short-drain `\"hel\"` plus queued `\"lo\"` helper boundary
* the non-destructive `snapshotInto()` cue
* preview and wrapped-preview boundaries
* `available()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()`
* the bounded `init()` -> `runAnchorReplay()` -> `exit()` ownership path

When a change touches the kobject packet, keep these cues explicit:

* sample-owned `runPreRegistrationBoundaryReplay()`
* sample-owned `runRegisteredBoundaryReplay()`
* sample-owned `runInputValidationReplay()`
* `ownershipSummary()` plus sample-owned `runOwnershipReplay()`
* sample-owned `runTeardownReplay()`
* the `abandoned_before_registration` versus `tore_down_registered_attributes` split

When a change touches the kretprobe packet, keep these cues explicit:

* sample-owned `runRetargetReplay()`
* sample-owned `runLifecycleGuardReplay()`
* the fixed `maxactiveBudget()` cue
* `ownershipSummary()` lifecycle snapshots across `cold`, `initialized`, `armed`, `replay_complete`, and `exited`
* sample-owned `runRecoveryReplay()`

When a change touches the trace-events packet, keep these cues explicit:

* `formattedMessage()`
* public `runPayloadBoundaryReplay()`
* public `runConditionalBoundaryReplay()`
* public `runCallbackBoundaryReplay()`
* the exact `checked_focus` order
* registration-balance cues
* `ownershipSummary()` plus sample-owned `runOwnershipReplay()`
* post-exit replay rejection

## Boundary reminders

Phase 5 stays non-runtime on current `master`.

Do not treat the later runtime pilot family as extra Phase 5 samples:

* `samples/zigux/runtime_atomic64.zig`
* `samples/zigux/runtime_atomic64_loader.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_kretprobe.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_loader.zig`

Keep these no-extra-sample reminders explicit too:

* there is no standalone `samples/zigux/*string*` Phase 5 reference sample; keep string-helper reviewability under the Phase 7 `string_helpers` packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under the Phase 7 `cmdline` packet
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under the Phase 7 `argv_split` packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under the Phase 7 packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample; keep direct bitmap helper reviewability under the closed Phase 1 plus Phase 4 packet while the runtime bitmap family stays in Phase 9
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` remains the approved formatting idiom cue

Respect the freeze map too. Do not widen Phase 5 sample work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 sample change, confirm:

* the sample descriptor still names the correct Linux anchor
* the paired manifest still matches the sample contract
* the survey note still describes the same exact replay
* `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still describe the same four-sample non-runtime packet
* the change keeps runtime-substrate claims out of scope unless a later roadmap-backed lane explicitly reopens them

## Non-goals

This shared Phase 5 guide does not claim:

* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure
