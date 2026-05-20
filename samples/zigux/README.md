# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-20 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kobject_example_attr_group_contract.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

## Phase 5 reminder

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` still keeps the roadmap-backed `kobject` packet visible through public current-`master` readback for `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, and `zigux/tests/phase5_build.zig`, even though authenticated contents reread for those same paths still flakes in this runtime.

Keep that kobject packet framed as the approved in-memory ownership-and-lifetime idiom for the Phase 5 anchor:

* `runPreRegistrationBoundaryReplay()` keeps the initialized-but-not-registered zero-active-attributes boundary explicit
* `ownershipSummary()` plus sample-owned `runOwnershipReplay()` keep the cold, initialized, registered, and exited lifecycle cues explicit
* keep the initialized-only `abandoned_before_registration` exit split distinct from the registered `tore_down_registered_attributes` teardown path
* keep sysfs file creation, `kernel_kobj` integration, uevents, and module registration out of scope

Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.

Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.

## Phase 9 runtime pilot family

The surviving direct runtime-module sample packet in this directory is still centered on `samples/zigux/runtime_trace_events.zig`.

Fresh trusted mixed reread on 2026-05-20 also restored a narrower runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` still remain absent on the same trusted path. Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.

Keep `samples/zigux/runtime_bitmap.zig` explicit as the bounded two-word in-memory bitmap starter proof with selftest-hook metadata, sparse iteration, parse-and-print replay, range mutation, copy behavior, and direct exit guards. Keep `samples/zigux/runtime_bitmap_top_bit_contract.zig` explicit as the returned highest-valid-bit companion proof for the same runtime bitmap starter. Keep the still-missing loader, module, diff, and manifest legs framed as same-family backlog surfaces until a fresh trusted reread returns them directly again.

## No-extra-sample reminders

Current `master` still ships no standalone Phase 5 sample-root files here for:

* `*string*`
* `*cmdline*`
* `*argv*`
* `*rbtree*`
* `*kasprintf*`
* `*strarray*`
* `*bitmap*`
* `*printf*`
* `*vsprintf*`
* `*format*`
