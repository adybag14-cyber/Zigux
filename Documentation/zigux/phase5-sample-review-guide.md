# Phase 5 Sample Review Guide

This guide keeps the shipped Phase 5 reference-sample packet reviewable from one place.

Use it when a change touches more than one Phase 5 sample surface, when a reviewer needs the shared packet map instead of a single survey note, or when a contributor needs to decide whether a change still belongs in the non-runtime Phase 5 lane instead of the separate Phase 9 `samples/zigux/runtime_*` family.

## Shared packet

The current shared Phase 5 packet on `master` is:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- the four survey notes under `Documentation/zigux/`
- the four sample modules under `samples/zigux/`
- the four focused sample replays, the four manifest files, and the four survey gates under `zigux/tests/`
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
- the explicit `StorageBacking.embedded_fixed_buffer` cue so the approved idiom stays reviewable as a bounded fixed-buffer ring instead of reading like an allocation-backed or runtime-substrate queue
- the bounded preview and rollover cues around `previewInto()`, `available()`, and `usesWrappedStorageWindow()`, plus the `visibleSpanSummary()` split cue that keeps the fixed-buffer ring shape reviewable instead of implicit

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
- `runPreRegistrationBoundaryReplay()` for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary
- `runRegisteredBoundaryReplay()` for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward
- `runInputValidationReplay()` for the shared `baz`/`bar` dispatch plus parse-failure visibility while the sample stays registered
- `ownershipSummary()` plus sample-owned `runOwnershipReplay()` for the `cold`, `initialized`, `registered`, and `exited` lifecycle packet
- the init/register/exit counter progression inside `runOwnershipReplay()`, keeping the bounded ownership path visible as `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- `runTeardownReplay()` for the registered teardown reset plus post-`exit()` show-or-store, second-`exit()`, and anchor-replay rejection cues
- the unnamed attribute-group shape
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
- `runRetargetReplay()` plus pre-init retargeting, empty-symbol rejection, and post-init retarget rejection
- `runAnchorReplay()` plus kernel-thread skip behavior, the one-word private entry timestamp cue, return value `42`, duration `75 ns`, and the missed-instance summary contract
- `runLifecycleGuardReplay()` plus the pre-init and post-init guard boundaries, including the pre-init anchor and exit rejections plus double-init rejection
- the fixed `maxactiveBudget()` cue at `20`
- `ownershipSummary()` plus sample-owned `runOwnershipReplay()` for the `cold`, `initialized`, `armed`, `replay_complete`, and `exited` lifecycle snapshots with active-instance and entry-timestamp state
- `runRecoveryReplay()` plus outstanding-instance rejection, the recovered duration `60 ns`, and the sample-owned teardown recovery packet
- timestamp-order rejection and recovery plus post-exit handler rejection

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
- the public `runConditionalBoundaryReplay()` helper plus the count-0 `Mother Goose` branch, the count-5 wraparound back to `Mother Goose`, the selected-string boundary, the `iter=%d` replay, the `0xdeadbeef` bitmask cue, and six main-thread family counts without private sample-state reads
- vararg-payload and relative-location markers in the public replay summary
- the exact `checked_focus` order
- the public `runCallbackBoundaryReplay()` helper plus the explicit callback-path replay, the registration depth rising to `1` after register and returning to `0` after unregister, and the bounded `init()` -> replay helpers -> `exit()` ownership path
- `ownershipSummary()` plus sample-owned `runOwnershipReplay()` for the public `cold`, `initialized`, `replay_complete`, and `exited` lifecycle packet, the final selected-string plus `iter=%d` snapshot, and the restored callback-registration balance
- `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection
- post-exit replay and callback-registration rejection so the sample stays a bounded ownership-and-lifetime example instead of only a tracing example
- the docs-root and sample-root contributor surfaces in `Documentation/zigux/README.md` and `samples/zigux/README.md` should keep those same formatting, conditional-family, callback-boundary, public ownership-helper, and Phase 5-versus-Phase 9 cues aligned, while `scripts/zigux/README.md` and `zigux/tests/README.md` should keep the shared replay route, sample-backed packet, and Phase 5-versus-Phase 9 split explicit instead of leaving the trace-events packet isolated to this note

Keep out of scope
- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Contributor refresh sequence

1. Start with the sample file and its directly coupled survey note.
2. If the contract changed, update the manifest and the paired survey test in the same edit.
3. If the change moves a shared boundary, refresh `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, this guide, and `Documentation/zigux/review-checklist.md` together instead of leaving the packet split across per-sample notes.
4. If the change touches `bytestream_fifo`, recheck the sample-local survey note, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared `phase5_build.zig` route so `StorageBacking.embedded_fixed_buffer`, the queue-order drain contract, the non-destructive `snapshotInto()` cue, the short-drain `"hel"` plus queued `"lo"` helper boundary, the bounded preview and rollover cues around `previewInto()`, `available()`, `usesWrappedStorageWindow()`, and `visibleSpanSummary()`, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path stay synchronized across the note, guide, checklist, and shared packet map.
5. If the change touches `kobject_example`, recheck the sample-local survey note, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_survey.zig`, and the shared `phase5_build.zig` route so `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, `runTeardownReplay()`, the init/register/exit counter progression, the unnamed attribute-group shape, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split stay synchronized across the note, guide, checklist, and shared packet map.
6. If the change touches `kretprobe_example`, recheck the sample-local survey note, `zig test samples/zigux/kretprobe_example.zig`, the focused `zigux/tests/phase5_kretprobe_example.zig` boundary replay, and the shared `phase5_build.zig` route so `runRetargetReplay()`, `runLifecycleGuardReplay()`, the fixed `maxactiveBudget()` cue, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, and `runRecoveryReplay()` do not drift apart across the note, guide, checklist, and shared packet map.
7. If the change touches `trace_events_sample`, recheck the sample-local survey note, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zig test --test-no-exec zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `phase5_build.zig` route so the manifest-backed provenance, `formattedMessage()` formatting boundary, the public `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, and `runCallbackBoundaryReplay()` helpers, the no-standalone-format-sample reminder, and the ownership-replay guidance stay synchronized across the note, guide, checklist, and shared packet map.
8. Re-run the shared Phase 5 replay route through `zigux/tests/phase5_build.zig`.
9. Keep the shared packet distinct from the separate Phase 9 runtime starters and loader-side follow-ons.

## Boundary reminders

- The four shipped Phase 5 samples are the whole current reference-sample packet; later `samples/zigux/runtime_*` files belong to Phase 9.
- The same four anchors are the full freeze-aware scope for this lane; do not propose `samples/zigux/` follow-ons rooted in `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and keep the study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` families out of the Phase 5 packet.
- If a sample follow-up needs runtime loader wiring, scheduler participation, workqueue handoff, ring-buffer substrate, or other non-sample kernel execution context to make its contract honest, route that work to the separate Phase 9 or Phase 14 packets instead of widening this four-sample guide.
- Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference sample.
- Current `master` still ships no standalone `samples/zigux/*string*` Phase 5 reference sample; keep string-helper reviewability under `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, and `zigux/tests/phase7_build.zig` instead of treating string helpers as a fifth Phase 5 sample.
- Current `master` still ships no standalone `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, and `zigux/tests/phase7_build.zig` instead of treating cmdline as a fifth Phase 5 sample.
- Current `master` still ships no standalone `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `scripts/zigux/check-phase7-argv-split-packet.py`, and `zigux/tests/phase7_build.zig` instead of treating `argv_split` as a fifth Phase 5 sample.
- Current `master` still ships no standalone `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig` instead of treating `rbtree` as a fifth Phase 5 sample.
- Keep direct bitmap helper reviewability under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, and `Documentation/zigux/phase4-validation-matrix.md` instead of counting bitmap as a fifth Phase 5 sample.
- Keep the separate runtime bitmap family under `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` instead of treating bitmap as a shared Phase 5 approved idiom.
- Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue.
- Formatting-helper reviewability still stays with the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet; do not infer a fifth formatting sample from `trace_events_sample`.

## Next-step rule

If a future run reopens this shared guide, keep the follow-through limited to the next smallest contributor-guidance or replay-contract alignment step that helps reviewers navigate the four shipped Phase 5 samples without implying runtime-substrate closure.
