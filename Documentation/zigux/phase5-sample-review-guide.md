# Phase 5 Sample Review Guide

This guide keeps the shipped Phase 5 reference-sample packet reviewable from one place.

Use it when a change touches more than one Phase 5 sample surface, when a reviewer needs the shared packet map instead of a single survey note, or when a contributor needs to decide whether a change still belongs in the non-runtime Phase 5 lane instead of the separate Phase 9 `samples/zigux/runtime_*` family.

## Shared packet

The current shared Phase 5 packet on `master` is:

- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- the four survey notes under `Documentation/zigux/`
- the four sample modules under `samples/zigux/`
- the four manifest-backed test packets under `zigux/tests/`
- `zigux/tests/phase5_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

The shipped replay routes for that packet are:

- `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
- `make -C zigux phase5-test`
- `make -C zigux phase5`

Current `master` still ships no shared `validate-phase5.py`, no `check-phase5-*.py` checker packet, and no `phase5-validate` target. Keep Phase 5 follow-through inside sample-backed contributor guidance or exact replay-contract repairs unless a new shipped validation surface lands first.

## Sample map

### `bytestream_fifo`

Linux anchor
- `samples/kfifo/bytestream-example.c`

Primary Phase 5 packet
- `samples/zigux/bytestream_fifo.zig`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`

Keep explicit
- the exact queue-order drain contract
- the non-destructive `snapshotInto()` cue
- the short-drain `"hel"` plus queued `"lo"` helper boundary
- the `init()` -> `runAnchorReplay()` -> `exit()` ownership path
- the bounded preview and rollover cues around `previewInto()`, `available()`, and `usesWrappedStorageWindow()`

Keep out of scope
- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- locking or blocking semantics
- loadable module registration

### `kobject_example`

Linux anchor
- `samples/kobject/kobject-example.c`

Primary Phase 5 packet
- `samples/zigux/kobject_example.zig`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

Keep explicit
- the initialized-but-not-registered zero-active-attributes boundary
- `ownershipSummary()` plus sample-owned `runOwnershipReplay()`
- the unnamed attribute-group shape
- shared `baz` or `bar` dispatch
- the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split

Keep out of scope
- sysfs file creation parity
- `kernel_kobj` integration
- uevents
- loadable module registration

### `kretprobe_example`

Linux anchor
- `samples/kprobes/kretprobe_example.c`

Primary Phase 5 packet
- `samples/zigux/kretprobe_example.zig`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

Keep explicit
- pre-init retargeting
- `runLifecycleGuardReplay()` plus the pre-init and post-init guard boundaries
- the fixed `maxactiveBudget()` cue at `20`
- `runRecoveryReplay()` plus outstanding-instance rejection
- timestamp-order rejection and recovery plus post-exit handler rejection
- the sample-owned lifecycle summary packet

Keep out of scope
- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- runtime module wiring

### `trace_events_sample`

Linux anchor
- `samples/trace_events/trace-events-sample.c`

Primary Phase 5 packet
- `samples/zigux/trace_events_sample.zig`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Keep explicit
- `formattedMessage()`, the selected-string plus `iter=%d` replay, and the public `runPayloadBoundaryReplay()` formatting cue
- vararg-payload and relative-location markers in the public replay summary
- the exact `checked_focus` order
- the public `runCallbackBoundaryReplay()` helper plus the explicit callback-path replay and balanced register-then-unregister callback flow
- `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection
- post-exit replay rejection

Keep out of scope
- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Contributor refresh sequence

1. Start with the sample file and its directly coupled survey note.
2. If the contract changed, update the manifest and the paired survey test in the same edit.
3. If the change moves a shared boundary, refresh `samples/zigux/README.md`, this guide, and `Documentation/zigux/review-checklist.md` together instead of leaving the packet split across per-sample notes.
4. Re-run the shared Phase 5 replay route through `zigux/tests/phase5_build.zig`.
5. Keep the shared packet distinct from the separate Phase 9 runtime starters and loader-side follow-ons.

## Boundary reminders

- The four shipped Phase 5 samples are the whole current reference-sample packet; later `samples/zigux/runtime_*` files belong to Phase 9.
- Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference sample.
- Keep direct bitmap helper reviewability under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, and `Documentation/zigux/phase4-validation-matrix.md` instead of counting bitmap as a fifth Phase 5 sample.
- Keep the separate runtime bitmap family under `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_build.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` instead of treating bitmap as a shared Phase 5 approved idiom.
- Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue.
- Formatting-helper reviewability still stays with the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet; do not infer a fifth formatting sample from `trace_events_sample`.

## Next-step rule

If a future run reopens this shared guide, keep the follow-through limited to the next smallest contributor-guidance or replay-contract alignment step that helps reviewers navigate the four shipped Phase 5 samples without implying runtime-substrate closure.
