# Phase 5 Sample Review Guide

This note is the shared contributor guide for the landed non-runtime Phase 5 reference-sample packet.

## Scope

Phase 5 stays limited to the four approved sample-backed Zigux idiom anchors:

- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Keep the paired review packet aligned with the same shared surfaces already named from the docs root, scripts root, and tests root:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Use `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, and `make -C zigux phase5` as the shared replay route for the four-sample packet.

`.github/workflows/zigux-bootstrap.yml` currently reruns only the direct `zig build test --build-file zigux/tests/phase5_build.zig --summary all` command, while `make -C zigux phase5-test` and `make -C zigux phase5` remain local Linux-style wrappers over that same shared build entrypoint.

The three focused direct replays that currently sit beside that shared packet are `zig test samples/zigux/bytestream_fifo.zig` for the bytestream FIFO sample-owned queue-order and ownership cues, `zig test samples/zigux/kretprobe_example.zig` for the sample-owned kretprobe cue set, and `zig test --test-no-exec zigux/tests/phase5_trace_events_sample_survey.zig` for the trace-events survey gate. Keep those sample-local commands aligned with the per-sample survey notes and the shared `phase5_build.zig` route instead of implying a separate `phase5-validate` lane.

## Review Cues

### `bytestream_fifo`

Keep the sample-backed review packet explicit around the queue-order drain contract, the non-destructive `snapshotInto()` cue, the short-drain `\"hel\"` plus queued `\"lo\"` helper boundary, the `StorageBacking.embedded_fixed_buffer` fixed-buffer ring cue, the bounded preview and rollover cues around `previewInto()`, `available()`, and `usesWrappedStorageWindow()`, the `visibleSpanSummary()` split cue, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path.

### `kobject_example`

Keep the sample-backed review packet explicit around initialized-but-not-registered access rejection, duplicate-registration and replay-restart rejection after registration, the bounded `foo` roundtrip, shared `baz` or `bar` input validation, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, the registered teardown reset, the post-`exit()` show-or-store rejection packet, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split.

### `kretprobe_example`

Keep the sample-backed review packet explicit around pre-init retargeting, empty-symbol and post-init retarget rejection, the fixed `maxactiveBudget()` cue, `ownershipSummary()` lifecycle snapshots across `cold`, `initialized`, `armed`, `replay_complete`, and `exited`, timestamp-order rejection and recovery, and post-exit replay rejection.

### `trace_events_sample`

Keep the sample-backed review packet explicit around the selected-string plus `iter=%d` formatting cue, the public `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, and `runCallbackBoundaryReplay()` helpers, the exact `checked_focus` order, relative-location and vararg-payload markers, registration-balance cues, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and post-exit replay rejection.

## Contributor Rules

When a landed Phase 5 sample changes, update the directly coupled review surfaces in the same patch:

- the paired survey note under `Documentation/zigux/`
- the paired manifest-backed replay packet under `zigux/tests/`
- any shared checklist or docs-root wording that names the exact replay contract
- the shared `zigux/tests/phase5_build.zig` route when the executable review surface changes

Keep Phase 5 reviewability sample-backed and small. Do not present later runtime-substrate work as if it already landed here.

## Boundaries

Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample. Treat the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet.

Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` Phase 5 reference sample. Keep those review surfaces under their existing helper-owned packets instead of counting them as extra Phase 5 samples:

- `Documentation/zigux/phase7-string-helpers-slice.md` plus `lib/string_helpers.zig`
- `Documentation/zigux/phase7-cmdline-slice.md` plus `lib/cmdline.zig`
- `Documentation/zigux/phase7-argv-split-slice.md` plus `lib/argv_split.zig`
- `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`
- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase4-validation-matrix.md`, and `tools/lib/bitmap.zig` for direct bitmap helper reviewability

Keep the later `samples/zigux/runtime_atomic64*.zig`, `runtime_bitmap*.zig`, `runtime_kretprobe*.zig`, and `runtime_trace_events*.zig` families in the separate Phase 9 runtime lane instead of implying runtime-substrate closure from the shared Phase 5 review route.

## Non-goals

This guide does not turn the Phase 5 packet into runtime parity for procfs, user-copy, sysfs creation, `kernel_kobj`, uevents, `pt_regs`, tracepoint macros, callback scheduling, kernel registration, or module wiring. Keep those boundaries explicit whenever Phase 5 contributor guidance changes.
