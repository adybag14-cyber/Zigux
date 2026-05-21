# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-21 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kobject_example_attr_group_contract.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
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

Current `master` also keeps the direct non-runtime bytestream packet visible as current sample-root proof through directly readable paired evidence for `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`, while `zigux/tests/phase5_build.zig` stays current public-tree-backed companion evidence until a fresh authenticated reread returns that shared route directly again.

Keep that bytestream packet framed as the approved in-memory FIFO idiom for the Phase 5 anchor:

* `BytestreamFifoSample.descriptor()` keeps the Linux anchor path, `requires_runtime_substrate = false`, `provides_selfcheck = true`, and `StorageBacking.embedded_fixed_buffer` explicit
* the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle keeps queue ownership and lifetime reviewable without implying runtime-owned registration
* `runPreviewBoundaryReplay()` plus `runWrappedPreviewReplay()` keep non-destructive preview truncation and the wrapped `{ 28, 4 }` visible-span split explicit at the sample root
* `runRemainingCapacityReplay()` plus `runPartialEnqueueBoundaryReplay()` keep `available()`, occupancy and writable-span cues, the short-drain `"hel"` / `"lo"` helper boundary, and partial `enqueueSlice()` truncation explicit
* `zig test samples/zigux/bytestream_fifo.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay explicit as the sample-owned self-check, focused replay, and survey guard routes, while `zigux/tests/phase5_build.zig` remains current public-tree-backed companion evidence only
* keep procfs, user-copy, locking, and loadable module registration parity out of scope

Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example.zig` are direct authenticated reminder or packet evidence again, `zigux/tests/phase5_build.zig` is the current directly readable shared build-route companion for that packet, and `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those three routes directly again.

Keep that kobject packet framed as the approved in-memory ownership-and-lifetime idiom for the Phase 5 anchor:

* `runSingleInitBoundaryReplay()` keeps the one-time `init()` rule plus the `1/0/0` counter posture explicit before registration begins
* `runPreRegistrationBoundaryReplay()` keeps the initialized-but-not-registered zero-active-attributes boundary explicit
* `runRegistrationOwnershipReplay()` plus `runRegisteredBoundaryReplay()` keep the cold-to-initialized-to-registered handoff, duplicate-registration rejection, and the still-usable registered-stage foo roundtrip explicit
* `runInputValidationReplay()` plus `ownershipSummary()` and sample-owned `runOwnershipReplay()` keep the shared `baz`/`bar` dispatch, parse-failure visibility, and the cold, initialized, registered, and exited lifecycle cues explicit
* keep the initialized-only `abandoned_before_registration` exit split distinct from the registered `tore_down_registered_attributes` teardown path
* keep sysfs file creation, `kernel_kobj` integration, uevents, and module registration out of scope

Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.

Keep the kobject anchor framed as a roadmap-backed Phase 5 target with the current mixed packet explicit in this runtime: `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example.zig` are direct reminder or packet evidence again, `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for that packet, and `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` stay public-tree-backed companion evidence until a fresh authenticated reread returns those three routes directly. Keep shared contributor guidance honest about that split-readback packet instead of repeating the older kobject-reread-needed sample-root wording, collapsing the packet into repo absence, or overstating fully direct authenticated proof.

Current `master` also keeps the direct non-runtime kretprobe packet visible as current direct sample-root proof through directly readable paired test evidence for `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`.

Keep that kretprobe packet framed as the approved in-memory handler and teardown idiom for the Phase 5 anchor:

* `runAnchorReplay()` keeps skipped kernel-thread handling, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and replay `maxactive = 20` explicit
* pre-init `retargetSymbol("do_sys_openat2")` and `retargetMaxactive(3)` stay explicit as in-memory choices, with empty-symbol and zero-value rejection, rather than as `module_param` or runtime registration parity
* the focused test pair keeps outstanding-instance exit rejection, recovered duration `60`, `entry_stamp_ns = -1` reset, and post-exit `recordMissedInstance()` rejection explicit
* `zig test samples/zigux/kretprobe_example.zig`, `zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig`, and `zig test zigux/tests/phase5_kretprobe_example_survey.zig` stay explicit as the sample-owned self-check, focused replay, and survey guard routes, while `zigux/tests/phase5_build.zig` remains current public-tree-backed companion evidence only
* keep `register_kretprobe`, `unregister_kretprobe`, `pt_regs or regs_return_value`, and loadable module wiring out of scope

Current `master` also keeps the bounded non-runtime trace-events packet visible through the direct formatting companion `samples/zigux/trace_events_string_formatting_sample.zig` together with the shared Phase 5 reminder packet.

Keep that trace-events packet framed as the approved selected-string plus `iter=%d` formatting idiom for the Phase 5 anchor:

* `samples/zigux/trace_events_string_formatting_sample.zig` stays the direct sample-root proof for the bounded formatting companion rather than a returned full trace-events port or a fifth sample
* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shared reminder packet explicit for the same narrow trace-events posture
* `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay broader public-tree-backed companion or historical-support evidence until a fresh authenticated reread returns them directly again
* keep Phase 9 runtime trace-events files out of this non-runtime Phase 5 proof packet

For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly. Keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence rather than direct authenticated proof.

Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.

## Phase 9 runtime pilot family

The surviving direct runtime-module sample packet in this directory is still centered on `samples/zigux/runtime_trace_events.zig`.

Keep `samples/zigux/runtime_trace_events.zig` explicit as the direct runtime sample, including the rejected re-selftest rollback proof that keeps both selftest-complete and exited summaries stable when `runSelftest()` is retried out of lifecycle order.
Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the unregistered function-thread fail-closed companion for the same direct runtime packet.
Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback companion for the selftest-ready proof plus both the initialized no-direct-activity and initialized direct-activity lifecycle proofs in the same packet.
Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion, including the initialized direct-activity clean-exit proof without selftest.

Fresh trusted mixed reread on 2026-05-20 also restored a narrower runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `zigux/tests/runtime_bitmap_manifest.json`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit, and `zigux/tests/runtime_bitmap_module.zig` plus `zigux/tests/runtime_bitmap_diff.zig` still remain absent on the same trusted path. Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.

Keep `samples/zigux/runtime_bitmap.zig` explicit as the bounded two-word in-memory bitmap starter proof with selftest-hook metadata, sparse iteration, parse-and-print replay, range mutation, copy behavior, and direct exit guards. Keep `samples/zigux/runtime_bitmap_loader.zig` explicit as the returned loader-input companion proof for the same runtime bitmap starter. Keep `samples/zigux/runtime_bitmap_top_bit_contract.zig` explicit as the returned highest-valid-bit companion proof for the same runtime bitmap starter. Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family. Keep the neighboring `zigux/tests/phase9_build.zig` route names framed only as bounded rerun handles for the visible sample, loader, survey, top-bit, and manifest-backed packet while the module and diff legs stay absent on the trusted path. Keep the still-missing module and diff legs framed as same-family backlog surfaces until a fresh trusted reread returns them directly again.

## No-extra-sample reminders

Current `master` still ships no standalone Phase 5 sample-root files here for:

* `*string*`
* `*kasprintf*`
* `*strarray*`
* `*cmdline*`
* `*argv*`
* `*rbtree*`
* `*bitmap*`
* `*printf*`
* `*vsprintf*`

Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.

Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.

Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, printf, vsprintf, or broad format samples have landed here.
