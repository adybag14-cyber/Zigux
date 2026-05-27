# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-25 confirmed these current sample-root reminder-packet files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/bytestream_fifo_window_contract.zig`
* `samples/zigux/kobject_example_attr_group_contract.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/kretprobe_example_instance_budget_contract.zig`
* `samples/zigux/kretprobe_example_probe_spec.zig`
* `samples/zigux/trace_events_callback_focus_contract.zig`
* `samples/zigux/trace_events_payload_preview_contract.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_atomic64.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_direct_init_contract.zig`
* `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_kretprobe.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`
* `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
* `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`

## Phase 5 reminder

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` also keeps the direct non-runtime bytestream packet visible as current sample-root proof through directly readable paired evidence for `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, `samples/zigux/bytestream_fifo_window_contract.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`, while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.

Keep that bytestream packet framed as the approved in-memory FIFO idiom for the Phase 5 anchor:

* `BytestreamFifoSample.descriptor()` keeps the Linux anchor path, `requires_runtime_substrate = false`, `provides_selfcheck = true`, and `StorageBacking.embedded_fixed_buffer` explicit
* the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle keeps queue ownership and lifetime reviewable without implying runtime-owned registration
* `runPreviewBoundaryReplay()` plus `runWrappedPreviewReplay()` keep non-destructive preview truncation and the wrapped `{ 28, 4 }` visible-span split explicit
* `runRemainingCapacityReplay()` plus `runPartialEnqueueBoundaryReplay()` keep `available()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()` queue-shape cues, the short-drain `"hel"` / `"lo"` helper boundary, and partial `enqueueSlice()` truncation explicit
* `samples/zigux/bytestream_fifo_window_contract.zig` keeps the stable two-window visible-span and writable-span reference pattern explicit through `referencePattern()`, `visible_windows`, `writable_windows`, and the non-destructive preview or rollover booleans instead of leaving those queue-window anchors implied by the broader sample alone
* `zig test samples/zigux/bytestream_fifo.zig`, `zig test samples/zigux/bytestream_fifo_window_contract.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay explicit as the sample-owned self-check, queue-window companion, focused replay, and survey guard routes, while `zigux/tests/phase5_build.zig` remains current directly readable shared build-route companion evidence that reruns the sample-owned self-checks, the queue-window companion, the focused replay packet, and the survey guard together
* keep procfs, user-copy, locking, and loadable module registration parity out of scope

Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again. The direct sample-root owner file `samples/zigux/kobject_example.zig` does not materialize on the current trusted read path, so keep that owner-path reminder historical rather than presenting it as a currently returned file.

Keep that kobject packet framed as the approved in-memory ownership-and-lifetime idiom for the Phase 5 anchor:

* `runSingleInitBoundaryReplay()` keeps the one-time `init()` rule plus the `1/0/0` counter posture explicit before registration begins
* `runPreRegistrationBoundaryReplay()` keeps the initialized-but-not-registered zero-active-attributes boundary explicit
* `runRegistrationOwnershipReplay()` plus `runRegisteredBoundaryReplay()` keep the cold-to-initialized-to-registered handoff, duplicate-registration rejection, and the still-usable registered-stage foo roundtrip explicit
* `runInputValidationReplay()` plus `ownershipSummary()` and sample-owned `runOwnershipReplay()` keep the shared `baz`/`bar` dispatch, parse-failure visibility, and the cold, initialized, registered, and exited lifecycle cues explicit
* keep the initialized-only `abandoned_before_registration` exit split distinct from the registered `tore_down_registered_attributes` teardown path
* keep sysfs file creation, `kernel_kobj` integration, uevents, and module registration out of scope

Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.
Keep `zig test samples/zigux/kobject_example_attr_group_contract.zig` explicit as the companion-only validation route for that bounded attr-group packet while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kobject packet.
Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route that checks the companion, focused replay, and shared build-route markers together while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kobject packet.

Current `master` also keeps the direct non-runtime kretprobe packet visible as current direct sample-root proof through directly readable paired test evidence for `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`.

Keep that kretprobe packet framed as the approved in-memory handler and teardown idiom for the Phase 5 anchor:

* `runAnchorReplay()` keeps skipped kernel-thread handling, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and replay `maxactive = 20` explicit
* pre-init `retargetSymbol("do_sys_openat2")` and `retargetMaxactive(3)` stay explicit as in-memory choices, with empty-symbol and zero-value rejection, rather than as `module_param` or runtime registration parity
* `instanceBudgetContract()` keeps the `func` parameter name, `0o644` mode, default `kernel_clone`, one-word private-data shape, return-value and duration reporting, skipped-kernel-thread handling, and the `nmissed`-suggests-increasing-`maxactive` cue explicit for contributors reading the sample root
* the focused test pair keeps outstanding-instance exit rejection, recovered duration `60`, `entry_stamp_ns = -1` reset, and post-exit `recordMissedInstance()` rejection explicit
* `zig test samples/zigux/kretprobe_example.zig`, `zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig`, and `zig test zigux/tests/phase5_kretprobe_example_survey.zig` stay explicit as the sample-owned self-check, focused replay, and survey guard routes, while `zigux/tests/phase5_build.zig` remains current directly readable shared build-route companion evidence only
* keep `register_kretprobe`, `unregister_kretprobe`, `pt_regs or regs_return_value`, and loadable module wiring out of scope

Current `master` also ships `samples/zigux/kretprobe_example_instance_budget_contract.zig` as a bounded kretprobe companion. Keep that file framed as reviewability help for the Linux `func` parameter, shared `0o644` mode, default `kernel_clone`, one-word private-data shape, and the `nmissed` / `maxactive` cue rather than as a fifth Phase 5 sample family.
Keep `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig` explicit as the companion-only validation route for that bounded kretprobe packet while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kretprobe packet.
Keep `zig test --dep kretprobe_example_instance_budget_contract -Mroot=zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig -Mkretprobe_example_instance_budget_contract=samples/zigux/kretprobe_example_instance_budget_contract.zig` explicit as the focused replay route for that bounded kretprobe packet, while `zigux/tests/phase5_build.zig` keeps rerunning the sample-owned self-checks together with the focused replay, survey gate, and instance-budget companion checks for the broader kretprobe packet.

Current `master` also ships `samples/zigux/kretprobe_example_probe_spec.zig` as a bounded kretprobe companion. Keep that file framed as reviewability help for the direct Linux anchor path, default `kernel_clone` symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules rather than as a fifth Phase 5 sample family.
Keep `zig test samples/zigux/kretprobe_example_probe_spec.zig` explicit as the companion-only validation route for that bounded kretprobe packet while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kretprobe packet.
Keep `zig test --dep kretprobe_example_probe_spec -Mroot=zigux/tests/phase5_kretprobe_example_probe_spec.zig -Mkretprobe_example_probe_spec=samples/zigux/kretprobe_example_probe_spec.zig` explicit as the focused replay route for that bounded kretprobe packet, while `zigux/tests/phase5_build.zig` keeps rerunning the sample-owned self-checks together with the focused replay, survey gate, instance-budget companion checks, and probe-spec companion checks for the broader kretprobe packet.

Current `master` keeps the bounded non-runtime trace-events packet visible through the callback-focus companion `samples/zigux/trace_events_callback_focus_contract.zig`, the payload-preview companion `samples/zigux/trace_events_payload_preview_contract.zig`, the direct formatting companion `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder packet, while `samples/zigux/trace_events_sample.zig` stays historical or public-tree-backed companion evidence until a fresh authenticated reread returns it directly again.

Keep that trace-events packet framed as the approved selected-string plus `iter=%d` formatting idiom for the Phase 5 anchor:

* `samples/zigux/trace_events_string_formatting_sample.zig` stays the direct sample-root proof for the bounded formatting companion, `samples/zigux/trace_events_payload_preview_contract.zig` stays direct sample-root proof for the bounded payload-shape and conditional-event-family companion, and `samples/zigux/trace_events_sample.zig` stays broader public-tree-backed companion evidence rather than a returned full trace-events port or a fifth sample
* `samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` `checked_focus` order plus the callback-registration recovery cues explicit as trace-events reviewability help at the sample root rather than as a separate Phase 5 sample family
* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shared reminder packet explicit for the same narrow trace-events posture
* `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay broader public-tree-backed companion or historical-support evidence until a fresh authenticated reread returns them directly again
* keep Phase 9 runtime trace-events files out of this non-runtime Phase 5 proof packet

For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig`, the callback-focus contract at `samples/zigux/trace_events_callback_focus_contract.zig`, the payload-preview contract at `samples/zigux/trace_events_payload_preview_contract.zig`, and the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly. Keep the shared `zigux/tests/phase5_build.zig` route framed as current directly readable shared build-route companion evidence rather than as sample-local proof or as direct authenticated proof for the broader sample-local trace-events companion set.

Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.

## Phase 9 runtime pilot family

One direct runtime-module sample packet in this directory is centered on `samples/zigux/runtime_trace_events.zig`.

Keep `samples/zigux/runtime_trace_events.zig` explicit as the direct runtime sample, including the rejected re-selftest rollback proof that keeps both selftest-complete and exited summaries stable when `runSelftest()` is retried out of lifecycle order.
Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the unregistered function-thread fail-closed companion for the same direct runtime packet.
Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback companion for the selftest-ready proof plus both the initialized no-direct-activity and initialized direct-activity lifecycle proofs in the same packet.
Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion, including the initialized direct-activity clean-exit proof without selftest.
Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.
Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.
Keep the older `samples/zigux/runtime_trace_events_loader.zig` name framed as historical wider-family vocabulary instead of current sample-root proof. The surviving shared loader packet on current `master` is the narrower shared-owner surface carried by `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` shard, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` companion.

Current `master` also keeps a narrower returned runtime kretprobe sample-side packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes in `zigux/tests/phase9_build.zig`.
Keep that kretprobe packet framed as a bounded Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader substrate has closed or that loadable `register_kretprobe` parity already exists.
Keep `samples/zigux/runtime_kretprobe.zig` explicit as the direct runtime sample, including the selftest-hook path, reusable post-selftest probe replay, failed unregister rollback while a return instance is still active, and failed exit rollback while registration remains armed.
Keep `samples/zigux/runtime_kretprobe_loader.zig` explicit as the sample-side shared-request planning companion that keeps initialized-stage loader handoff, later selftest snapshot stability, and blocked selftest-complete shared-request boundaries reviewable, while the dedicated `phase9-runtime-kretprobe-loader-tests` route in `zigux/tests/phase9_build.zig` reruns that witness without treating it as proof of broader shared runtime-loader closure.
Keep `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig` explicit as the sample-side initialized-snapshot companion that proves the captured initialized lifecycle state survives later selftest and exit without drift, rather than as proof of live runtime-substrate closure.
Keep `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig` explicit as the sample-side registration-reentry companion that keeps reusable balanced probe cycles reviewable before selftest, after selftest, and fail-closed after exit without treating that guard as proof of broader shared runtime-loader closure.
The broader `zigux/tests/runtime_kretprobe_manifest.json` and `zigux/tests/runtime_kretprobe_diff.zig` references do not materialize on the trusted direct-read path in this runtime, so keep them out of the current sample-root packet until a fresh reread returns them.

Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit. Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.

Keep `samples/zigux/runtime_bitmap.zig` explicit as the bounded two-word in-memory bitmap starter proof with selftest-hook metadata, sparse iteration, parse-and-print replay, range mutation, copy behavior, and direct exit guards. Keep `samples/zigux/runtime_bitmap_direct_init_contract.zig` explicit as the returned direct-init normalization companion proof for the same runtime bitmap starter, covering unsorted duplicate input collapse, nth-set ordering, formatted sparse-summary stability, and lifecycle-summary stability through selftest and exit. Keep that direct-init companion framed as sample-root proof and as part of the shared `zigux/tests/phase9_build.zig` rerun bundle through the dedicated `phase9-runtime-bitmap-direct-init-contract-tests` route plus the aggregate `phase9-runtime-bitmap-tests` handle. Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter. Keep the shared `zigux/tests/phase9_build.zig` bundle framed as a rerun handle that now exercises that companion through the dedicated `phase9-runtime-bitmap-cold-stage-guard-tests` route plus the aggregate `phase9-runtime-bitmap-tests` handle. Keep `samples/zigux/runtime_bitmap_loader.zig` explicit as the returned loader-input companion proof for the same runtime bitmap starter. Keep `samples/zigux/runtime_bitmap_top_bit_contract.zig` explicit as the returned highest-valid-bit companion proof for the same runtime bitmap starter. Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family. Keep `zigux/tests/runtime_bitmap_module.zig` explicit as the module-side descriptor and lifecycle replay packet for the same runtime bitmap starter. Keep `zigux/tests/runtime_bitmap_diff.zig` explicit as the bounded diff-side summary replay packet for the same runtime bitmap starter. Keep the neighboring `zigux/tests/phase9_build.zig` route names framed only as bounded rerun handles for the visible sample, direct-init companion, cold-stage guard, loader, survey, top-bit, manifest-backed, module-side, and diff-side packet. Keep that broader bitmap-side visibility from being used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.

Keep the earlier non-owner boundary split explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot sample evidence.

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