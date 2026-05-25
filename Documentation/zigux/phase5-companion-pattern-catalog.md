# Phase 5 Companion Pattern Catalog

This note keeps the shipped Phase 5 companion files reviewable as bounded support material for the four approved non-runtime sample anchors.

## Purpose

Use this catalog when a Phase 5 change touches contributor guidance, review wording, or one of the sample-backed companion files that sharpen an approved anchor without creating a new sample family.

Phase 5 still stays inside these roadmap-backed anchors:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Keep the companion files below framed as reviewability help for those anchors rather than as standalone Phase 5 samples.

## Current companion packet

Current `master` ships these bounded Phase 5 companion files:

- `samples/zigux/bytestream_fifo_window_contract.zig`
- `samples/zigux/kobject_example_attr_group_contract.zig`
- `samples/zigux/kretprobe_example_instance_budget_contract.zig`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `samples/zigux/trace_events_callback_focus_contract.zig`

Keep the surrounding owner notes explicit too:

- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `samples/zigux/README.md`

## Reviewable roles

`samples/zigux/bytestream_fifo_window_contract.zig` keeps the queue-window reference pattern explicit for the `kfifo` anchor through stable visible-span and writable-span cues without turning queue-shape reviewability into a fifth sample family.

`samples/zigux/kobject_example_attr_group_contract.zig` keeps the bounded `foo` / `baz` / `bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot explicit for the `kobject` anchor without widening into sysfs or module-registration claims.

`samples/zigux/kretprobe_example_instance_budget_contract.zig` keeps the `func` parameter, `0o644` mode, default `kernel_clone`, one-word private-data shape, and the `nmissed` / `maxactive` cue explicit for the non-runtime `kretprobe` anchor without implying runtime registration parity.

`samples/zigux/trace_events_string_formatting_sample.zig` keeps the selected-string plus `iter=%d` formatting cue explicit for the `trace_events` anchor.

`samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order explicit for the same `trace_events` anchor without turning callback reviewability into a fifth sample family.

## Validation cues

Keep the directly shipped companion-side validation routes explicit where current Phase 5 reminder surfaces already name them:

- `zig test samples/zigux/bytestream_fifo_window_contract.zig`
- `zig test samples/zigux/kobject_example_attr_group_contract.zig`
- `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig`
- `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig`
- `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig`
- `zig test --dep kretprobe_example_instance_budget_contract -Mroot=zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig -Mkretprobe_example_instance_budget_contract=samples/zigux/kretprobe_example_instance_budget_contract.zig`

Keep `zigux/tests/phase5_build.zig` framed as the shared rerun companion for the wider Phase 5 packet rather than as sample-local proof.

## Boundary reminders

Do not treat the companion packet as proof of:

- a fifth approved Phase 5 sample
- standalone helper-family sample delivery for `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, or `*vsprintf*`
- runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims

Keep `samples/zigux/runtime_*.zig` in the separate Phase 9 lane rather than using runtime files as extra Phase 5 evidence.

## Next bounded use

When a same-lane follow-up touches shared contributor guidance, reread this catalog together with `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py` before widening sample-local behavior claims.
