# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 sample lane reviewable without letting a stale shared reminder surface override newer direct packet proof.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or the shared tracing and probe reviewer surfaces.

The Phase 5 goal stays narrow:

* keep the approved Zigux idioms reviewable
* keep ownership and lifetime cues explicit
* keep exact review surfaces visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the same four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-19 confirmed that current `master` now directly serves the bounded bytestream sample-plus-tests packet through these paths:

* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/bytestream_fifo_window_contract.zig`
* `samples/zigux/bytestream_fifo_transfer_contract.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig`
* `zigux/tests/phase5_bytestream_fifo_manifest.json`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`

That same reread now directly returns the shared build-route companion for this bytestream packet too:

* `zigux/tests/phase5_build.zig`

Keep the direct bytestream sample-plus-tests packet explicit while the bounded queue-window companion `samples/zigux/bytestream_fifo_window_contract.zig` and the shared build-route companion stay framed as current directly readable packet evidence for the bytestream lane instead of flattening the packet back into a sample-only story or treating that shared build route as sample-local proof.
Fresh 2026-05-20 follow-up reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps five focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.
Keep the bounded queue-window companion explicit too: `samples/zigux/bytestream_fifo_window_contract.zig` now keeps the stable two-window visible-span and writable-span reference pattern reviewable through `referencePattern()`, `visible_windows`, `writable_windows`, and the non-destructive preview or rollover booleans instead of leaving that queue-shape contract implied by the broader sample alone.
Keep the bounded transfer-contract companion explicit too: `samples/zigux/bytestream_fifo_transfer_contract.zig` keeps the Linux-style transfer counts, the short-drain helper boundary, partial `enqueueSlice()` truncation, fixed-buffer backing, and the non-runtime posture reviewable at the sample root, while `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig` keeps the same transfer packet explicit as a focused replay instead of leaving it implicit in the sample-owned companion alone.

The same 2026-05-19 repo-first inspection also confirmed a narrower current non-runtime trace-events packet: authenticated contents reread still directly proves the bounded formatting companion, the bounded callback-focus companion, and the bounded payload-preview companion, and the shared reminder surfaces below still keep that smaller packet explicit:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/check-phase5-review-guide-surface.py`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/trace_events_callback_focus_contract.zig`
* `samples/zigux/trace_events_payload_preview_contract.zig`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Keep that narrower packet as the current concrete trace-events evidence in this lane.
Keep the bounded formatting companion explicit as a sibling cue inside the approved trace-events anchor rather than as a fourth returned direct sample-root port or a fifth sample.
Keep the bounded callback-focus companion explicit there too: it remains direct sample-root reviewability help for the same anchor rather than a returned full trace-events port or a fifth sample.
Keep the bounded payload-preview companion explicit there too: it remains direct sample-root reviewability help for payload-shape and conditional-event-family cues under the same anchor rather than a returned full trace-events port or a fifth sample.
Keep the broader sample-local companion split explicit too:

* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`

`Documentation/zigux/phase5-trace-events-sample-survey.md` is directly readable again on current `master` and should stay grouped with the shared reminder packet rather than the still-split broader sample-local companion set. The four broader sample-local companion paths remain public-tree-backed companion, repo-reality-gap, or historical support references on `master` until a fresh authenticated reread proves they returned directly. The shared `zigux/tests/phase5_build.zig` route now needs separate wording as current directly readable shared rerun evidence for that broader packet instead of companion-only support.
Fresh public current-`master` fallback on 2026-05-19 also keeps the broader four-file non-runtime trace-events sample-local companion packet visible through `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`, while `Documentation/zigux/phase5-trace-events-sample-survey.md` remains the directly readable survey note for that anchor. Same-lane guidance should therefore treat authenticated-contents `404` results there as connector-local readback flakiness instead of repo absence while keeping those four broader sample-local companions framed separately from the now-returned shared `zigux/tests/phase5_build.zig` rerun handle.
When contributors refresh a shared trace-events reminder, keep `Documentation/zigux/phase5-trace-events-sample-survey.md` listed as the directly readable survey note for that anchor, keep the four broader sample-local companions listed as current-master-visible companion evidence, and keep the shared `zigux/tests/phase5_build.zig` route classified separately as current directly readable shared rerun evidence rather than companion-only support.

For the shared tracing and probe lane, ground reviewer guidance in the restored direct kretprobe packet plus the narrower trace-events packet above and these shared reminder surfaces:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/check-phase5-review-guide-surface.py`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Keep those shared surfaces honest about the restored direct kretprobe packet, the bounded kretprobe instance-budget companion, the bounded kretprobe probe-spec companion, the bounded trace-events formatting companion, the bounded trace-events callback-focus companion, the bounded trace-events payload-preview companion, the directly readable trace-events survey note, the broader trace-events sample-local companions that are still visible through public-tree-backed reread but not yet returned as direct authenticated proof in this runtime, and the returned shared-build rerun handle instead of treating the trace-events anchor as either fully absent or fully restored authenticated proof.
Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` should stay aligned with those same shared surfaces instead of being treated as an optional companion.

## Bytestream posture

For `kfifo`, follow the restored direct sample-plus-tests packet through `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, `samples/zigux/bytestream_fifo_window_contract.zig`, `samples/zigux/bytestream_fifo_transfer_contract.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`.
Current `master` keeps that packet sharper than the older sample-only story: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps five focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the note and manifest.
Keep the bounded queue-window companion explicit too: `samples/zigux/bytestream_fifo_window_contract.zig` keeps the stable two-window visible-span and writable-span reference pattern reviewable through `referencePattern()`, `visible_windows`, `writable_windows`, and the non-destructive preview or rollover booleans instead of leaving that queue-shape contract implied by the broader sample alone.
Keep the bounded transfer-contract companion explicit too: `samples/zigux/bytestream_fifo_transfer_contract.zig` keeps the Linux-style transfer counts, the short-drain helper boundary, partial `enqueueSlice()` truncation, fixed-buffer backing, and the non-runtime posture reviewable at the sample root, while `zigux/tests/phase5_bytestream_fifo_transfer_contract.zig` keeps the same transfer packet explicit as a focused replay instead of leaving it implicit in the sample-owned companion alone.

Keep the current ten-cue review contract explicit in shared contributor guidance when a bytestream reminder surface is refreshed:

* `bounded_fifo_order`
* `wraparound_requeue`
* `peek_and_skip`
* `non_destructive_snapshot`
* `preview_truncation`
* `remaining_capacity`
* `queue_shape_boundaries`
* `helper_boundaries`
* `reset_and_replay`
* `ownership_and_lifetime`

Use the direct sample-plus-tests packet to keep the primary review surfaces visible too: `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle should stay easy to find from shared guidance instead of being left implicit in sample-local code only.
Keep the direct validation routes explicit in that same guidance too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test samples/zigux/bytestream_fifo_window_contract.zig`, `zig test samples/zigux/bytestream_fifo_transfer_contract.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, `zig test --dep bytestream_fifo_transfer_contract -Mroot=zigux/tests/phase5_bytestream_fifo_transfer_contract.zig -Mbytestream_fifo_transfer_contract=samples/zigux/bytestream_fifo_transfer_contract.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay visible as the sample-owned self-check route, the queue-window companion route, the transfer-contract companion route, the focused replay route, the focused transfer replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays visible as current directly readable shared build-route companion evidence for this bytestream packet rather than as sample-local proof.

Keep the current split explicit too:

* `zigux/tests/phase5_build.zig` is current directly readable shared build-route companion evidence for the bytestream packet, and it now reruns the sample-owned self-check route, the queue-window companion, the transfer-contract companion, the focused replay route, the focused transfer replay route, and the survey-packet guard together, but it still should not be treated as sample-local proof or as proof that broader trace-events companions returned directly
* same-lane follow-through should repair one reminder surface at a time instead of reclassifying the whole bytestream packet from memory or older wording alone
* the lane still stays non-runtime and should not widen into procfs, user-copy, locking, runtime loader, or module-registration claims

## Tracing and probe posture

For `kretprobe`, follow the restored direct packet recorded in `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while keeping `zigux/tests/phase5_build.zig` framed as current directly readable shared build-route companion evidence.
Keep `samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` explicit too as the bounded instance-budget companion and focused replay for the same anchor, so the shared guide keeps the Linux `func` parameter, shared `0o644` mode, default `kernel_clone`, one-word private-data shape, and `nmissed` / `maxactive` cue reviewable without leaving those details trapped in the dedicated survey note.
Keep `samples/zigux/kretprobe_example_probe_spec.zig` and `zigux/tests/phase5_kretprobe_example_probe_spec.zig` explicit too as the bounded probe-spec companion and focused replay for the same anchor, so the shared guide keeps the direct Linux anchor path, default symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules reviewable without leaving those details trapped in the dedicated survey note.

Keep the current kretprobe contributor cues explicit in shared guidance too:

* `samples/zigux/kretprobe_example.zig` keeps `kernel_clone` as the default symbol name while allowing pre-init `retargetSymbol("do_sys_openat2")`
* `zig test samples/zigux/kretprobe_example.zig`, `zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig`, and `zig test zigux/tests/phase5_kretprobe_example_survey.zig` stay explicit as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays current directly readable shared build-route companion evidence rather than sample-local proof
* `samples/zigux/kretprobe_example_instance_budget_contract.zig` plus `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` keep the bounded `func` parameter, shared `0o644` mode, default `kernel_clone`, one-word private-data shape, and `nmissed` / `maxactive` cue explicit beside the main replay packet instead of leaving that instance-budget reviewability trapped in the dedicated survey note alone
* `samples/zigux/kretprobe_example_probe_spec.zig` plus `zigux/tests/phase5_kretprobe_example_probe_spec.zig` keep the direct Linux anchor path, default symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules explicit beside the main replay packet instead of leaving that probe-spec reviewability trapped in the dedicated survey note alone
* `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zig test --dep kretprobe_example_instance_budget_contract -Mroot=zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig -Mkretprobe_example_instance_budget_contract=samples/zigux/kretprobe_example_instance_budget_contract.zig` stay explicit as the sample-owned companion route and focused replay route, while the shared `zigux/tests/phase5_build.zig` line stays current directly readable shared build-route companion evidence rather than sample-local proof and keeps rerunning both instance-budget checks beside the main kretprobe packet
* `zig test samples/zigux/kretprobe_example_probe_spec.zig` and `zig test --dep kretprobe_example_probe_spec -Mroot=zigux/tests/phase5_kretprobe_example_probe_spec.zig -Mkretprobe_example_probe_spec=samples/zigux/kretprobe_example_probe_spec.zig` stay explicit as the sample-owned companion route and focused replay route, while the shared `zigux/tests/phase5_build.zig` line stays current directly readable shared build-route companion evidence rather than sample-local proof and keeps rerunning both probe-spec checks beside the main kretprobe packet
* the direct packet keeps the pre-init-only `retargetMaxactive(3)` path, replay `maxactive = 20`, the single `my_data`-style entry timestamp word, the one-missed-instance summary, recovered duration `60`, and post-exit `recordMissedInstance()` rejection visible without implying runtime registration parity

For `trace_events`, follow the current bounded packet through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `samples/zigux/trace_events_callback_focus_contract.zig`, `samples/zigux/trace_events_payload_preview_contract.zig`, `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md` explicit as the directly readable survey note for that anchor, keep `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as public-tree-backed companion, repo-reality-gap, or historical support references until a fresh authenticated reread proves broader direct sample-local proof again on current `master`, and keep `zigux/tests/phase5_build.zig` explicit as the returned directly readable shared rerun route for that broader packet.

Use the shared docs to preserve these bounded cues:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` keeps the selected-string plus `iter=%d` formatting cue bounded to the trace-events packet instead of turning it into a fifth Phase 5 sample
* `samples/zigux/trace_events_string_formatting_sample.zig` keeps the sibling formatting companion explicit through `selectedStringForIteration(...)`, `runStringFormattingCycleReplay()`, the exact `iter=%d` buffer print, the modulo-selected five-string review cycle, and the non-allocating lifecycle boundary around the bounded replay instead of standing in for the whole trace-events packet
* `samples/zigux/trace_events_callback_focus_contract.zig` keeps the sibling callback-focus companion explicit through `anchorFocusOrder()`, `callbackBoundaryContract()`, the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order, plus the callback-registration recovery cues instead of turning that companion into a fifth Phase 5 sample
* `samples/zigux/trace_events_payload_preview_contract.zig` keeps the sibling payload-preview companion explicit through `referencePattern()`, the five-case modulo-selected preview ladder, the direct `conditional_event_families` cue, the `vararg_payload_path_checked` and `relative_location_path_checked` booleans, and the largest bounded preview case `"One ring to rule them all"` plus `"iter=4"` instead of turning that companion into a fifth Phase 5 sample
* `Documentation/zigux/phase5-trace-events-sample-survey.md` stays explicit as the directly readable survey note for that anchor, while `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay in repo-reality-gap or historical-support wording until authenticated contents reread stops returning 404 for those four sample-local companion paths, and `zigux/tests/phase5_build.zig` stays separately explicit as the returned directly readable shared rerun route
* `Documentation/zigux/phase5-sample-lane-sequencing.md`, `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shared reminder packet explicit about that narrower trace-events posture without widening into runtime claims
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` keep the restored non-runtime kretprobe packet explicit without widening into the Phase 9 runtime family

## Ownership and lifetime posture

The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback in this runtime directly returned `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and the shared build-route companion `zigux/tests/phase5_build.zig`, while the same reread also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion and fresh public current-`master` GitHub file readback kept `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` visible beside that direct packet. The same-lane survey note and shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when the authenticated contents route flakes on that one path.

Authenticated contents readback now directly returns these kobject packet members:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `zigux/tests/phase5_kobject_example.zig`

The same authenticated route also directly returns the shared build-route companion `zigux/tests/phase5_build.zig` for this packet.

The same reread also directly returns the bounded attr-group companion `samples/zigux/kobject_example_attr_group_contract.zig` for this packet.
The same reread also directly returns the focused attr-group replay `zigux/tests/phase5_kobject_attr_group_contract.zig` and the survey-guard companion `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` for that bounded packet.

Fresh public current-`master` fallback still carries these companion paths:

* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kobject_example_survey.zig`

Keep shared contributor guidance honest about that split instead of flattening the whole kobject packet into public-tree-only support material, treating the focused replay, shared build-route companion, or attr-group companion as gone, or promoting the survey note, manifest-backed contract, or survey replay into returned authenticated proof.

Use the shared docs to preserve these bounded cues while that mixed packet remains in place:

* Phase 5 still owns the roadmap-backed `samples/kobject/kobject-example.c` anchor
* `Documentation/zigux/phase5-kobject-sample-survey.md` and `zigux/tests/phase5_kobject_example.zig` are current direct reminder or packet evidence again, `zigux/tests/phase5_build.zig` is the current directly readable shared build-route companion for that packet, `samples/zigux/kobject_example_attr_group_contract.zig` stays the direct attr-group companion, the survey note plus surrounding shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner even when the current authenticated reread flakes on that one path, and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain the current public-tree-backed companion evidence
* the lane still stays non-runtime and should not widen into sysfs creation, `kernel_kobj` integration, uevents, or module-registration claims
* same-lane follow-through should repair one shared reminder surface at a time instead of recreating missing sample-local ownership checklists from historical wording alone

### `kobject_example`

When shared contributor guidance needs the current kobject packet, keep this mixed direct-plus-public-tree-backed packet explicit.

The directly readable packet members are:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `zigux/tests/phase5_kobject_example.zig`

The same direct readback also returns the shared build-route companion `zigux/tests/phase5_build.zig` and the bounded attr-group companion `samples/zigux/kobject_example_attr_group_contract.zig`.
The same-lane survey note and shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when the authenticated contents route flakes on that one path.

The current public-tree-backed companions are:

* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kobject_example_survey.zig`

Keep the approved Phase 5 in-memory ownership-and-lifetime idiom reviewable from the shared guide too:

* `runSingleInitBoundaryReplay()` keeps the one-time `init()` rule executable so a second `init()` still returns `InvalidLifecycleTransition` while the sample stays initialized with zero active attributes and `1/0/0` counters
* `runPreRegistrationBoundaryReplay()` keeps the initialized-but-not-registered zero-active-attributes boundary explicit before `registerAttributes()` opens the sample
* `runRegistrationOwnershipReplay()` keeps registration-before-init rejection, the cold-to-initialized-to-registered handoff, the active-attribute move from `0` to `3`, and duplicate `registerAttributes()` rejection executable instead of leaving registration ownership inferred from broader lifecycle prose
* `runRegisteredBoundaryReplay()` keeps duplicate-registration rejection, registered-stage replay rejection, and the still-usable registered-state `foo` write or read roundtrip explicit while the sample remains registered
* `runInputValidationReplay()` keeps the shared `baz` / `bar` dispatch, invalid-integer rejection, and unknown-attribute rejection explicit while the sample remains in the registered stage
* `ownershipSummary()` and sample-owned `runOwnershipReplay()` keep the cold, initialized, registered, and exited snapshots plus the active-attribute and `0/0/0` -> `1/0/0` -> `1/1/0` -> `1/1/1` counter progression visible from contributor-facing guidance
* `runTeardownReplay()` keeps the registered teardown reset, the post-`exit()` show/store/replay rejection packet, and the `tore_down_registered_attributes` exit disposition explicit instead of leaving the exited-stage packet implied by code alone
* `samples/zigux/kobject_example_attr_group_contract.zig` keeps the bounded `foo`/`baz`/`bar` attribute-group contract, the shared `0664` mode cue, the unnamed-group marker, and the NULL-terminated attribute-list slot explicit without turning that companion into a fifth Phase 5 sample
* `zig test samples/zigux/kobject_example.zig`, `zig test --dep kobject_example_sample -Mroot=zigux/tests/phase5_kobject_example.zig -Mkobject_example_sample=samples/zigux/kobject_example.zig`, and `zig test zigux/tests/phase5_kobject_example_survey.zig` stay explicit as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet
* `zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet
* keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit across the initialized-only exit path, the registered teardown path, and the broader post-`exit()` rejection packet

Keep the non-goal boundary equally explicit here:

* sysfs file creation parity
* `kernel_kobj` integration
* uevents
* loadable module registration

## Approved idiom gap

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.
Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample. Keep those helper-family reminders tied to their existing helper, closure, or later-phase packets instead of treating the sample root as proof they landed here.

Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by the trace-events review packet:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`

Do not describe that formatting cue as a fifth Phase 5 sample, a standalone formatting-helper port, or the whole proof of the trace-events packet.

## Review posture

Because current `master` keeps the restored direct bytestream sample-plus-tests packet, the restored bytestream transfer-contract companion and its focused replay, the restored direct kretprobe packet plus its bounded instance-budget companion and bounded probe-spec companion, the shared trace-events side in a narrower posture with direct formatting, callback-focus, and payload-preview companions plus older broader companion paths still in the repo-reality-gap bucket, and the `kobject` anchor in a mixed direct-plus-public-tree-backed split packet, same-lane follow-through should stay inside these bounded categories:

* one bytestream reminder-surface truthfulness repair at a time
* one trace-events reminder-surface truthfulness repair at a time
* one trace-events approved-idiom-gap repair at a time
* one trace-events survey-note, sample-root, tests-root, manifest, survey-replay, approved-idiom-gap, or shared-build reminder alignment repair at a time
* one kobject split-evidence reminder repair at a time
* one kretprobe sample, companion, focused replay, or shared-build reminder truthfulness repair at a time

Avoid:

* treating the returned bytestream build-route companion `zigux/tests/phase5_build.zig` as sample-local proof or as proof that the broader trace-events companion set returned directly
* treating the narrower trace-events packet as either fully absent or fully direct authenticated sample proof when current `master` still keeps the bounded formatting companion direct, the older broader sample-local companion paths missing from authenticated contents reread, and the shared `zigux/tests/phase5_build.zig` route in returned shared-rerun posture rather than as sample-local proof
* treating the returned bytestream build-route companion as permission to rewrite the broader trace-events or other cross-anchor reminder packet from memory instead of rereading the still-split surfaces first
* treating the whole `kobject` packet as fully direct authenticated proof when current rereads still leave `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` in the public-tree-backed companion bucket even though `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, the shared build-route companion `zigux/tests/phase5_build.zig`, and `samples/zigux/kobject_example_attr_group_contract.zig` are back on the direct authenticated path while `samples/zigux/kobject_example.zig` remains a sample-root owner cue carried by the survey note and surrounding shared reminder packet when the authenticated contents route flakes on that one path
* broadening the lane into runtime-loader, module-registration, procfs, sysfs, workqueue, ring-buffer, or other runtime-substrate claims
* treating Phase 9 runtime samples as extra Phase 5 evidence
* treating the trace-events packet as permission to reopen unrelated bytestream, kobject, or kretprobe reminder work here

## Boundary reminders
