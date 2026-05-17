# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-17 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`

The authenticated contents route used for this lane stayed flaky for part of the older Phase 5 packet during this reread, so the bytestream, kobject, kretprobe, and formatting-companion entries above were rechecked through a mix of authenticated contents readback and public-tree or raw-file fallback paths before this README was refreshed.

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` keeps the bytestream anchor reviewable through the sample-root port `samples/zigux/bytestream_fifo.zig`.
Current `master` also keeps the kobject anchor reviewable through the sample-root port `samples/zigux/kobject_example.zig`, while its broader focused-test and survey companions still need mixed-source wording when shared reminders mention them.
Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.
For the trace-events anchor, keep shared contributor guidance grounded in the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet until a fresh reread proves `samples/zigux/trace_events_sample.zig` has returned on current `master`.
Keep shared contributor guidance honest about that narrower packet instead of repeating the older broader direct-sample split.
Keep the bytestream and kobject anchors framed as concrete Phase 5 sample-root ports with mixed-source companion evidence rather than as absent sample-root targets.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream anchor, treat `samples/zigux/bytestream_fifo.zig` as the current sample-root proof for the roadmap-backed non-runtime lane and keep `Documentation/zigux/phase5-kfifo-sample-survey.md`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and the current public-tree-backed `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig` companions explicit.
When a shared Phase 5 guide, checklist, or README mentions the kobject anchor, treat `samples/zigux/kobject_example.zig` as the current sample-root proof for that non-runtime lane and keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` explicit while still describing `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` as current public-tree-backed companion evidence rather than direct authenticated-contents proof.
When a shared Phase 5 guide, checklist, or README mentions the kretprobe anchor, treat `samples/zigux/kretprobe_example.zig` as the current direct sample-root proof for the roadmap-backed non-runtime lane.
For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, and the paired shared reminder surfaces explicit instead of treating the older direct `samples/zigux/trace_events_sample.zig` path as current proof before a fresh reread restores it.

Keep `samples/zigux/trace_events_string_formatting_sample.zig` tied to the same non-runtime trace-events anchor as a bounded formatting companion.
Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.

Keep the shared `zigux/tests/phase5_build.zig` route in companion-evidence wording only when a fresh reread confirms that path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Phase 9 runtime pilot family

The surviving direct runtime-module sample packet in this directory is centered on `samples/zigux/runtime_trace_events.zig`.
Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `zigux/tests/README.md` aligned with that surviving direct runtime-module sample instead of reviving the removed shared loader packet by implication.

Keep the current direct runtime-module evidence explicit here too: `samples/zigux/runtime_trace_events.zig` still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking, so the separate runtime lane still has one shipped selftest-hook and lifecycle-parity sample-root proof on current `master`.

Keep saying clearly that current `master` does not currently expose the broader shared runtime-loader packet, so `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds stay backlog references unless a fresh repo reread proves they have returned; keep `.github/workflows/zigux-bootstrap.yml` named only as a shared repo-level workflow surface, not as dedicated Phase 9 evidence.

Keep older cross-phase non-owner boundaries explicit: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.

Treat `samples/zigux/runtime_trace_events_unregistered_gate.zig` as the same narrow runtime packet's fail-closed companion for unregistered function-thread failures and post-exit invalid-lifecycle rejections, including the initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks, not as proof that the broader shared loader family has returned.

## No-extra-sample reminders

Current `master` still ships no standalone Phase 5 sample-root files here for:

* `*string*`
* `*cmdline*`
* `*argv*`
* `*rbtree*`
* `*bitmap*`

Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, bitmap, `printf`, or `vsprintf` sample families landed here as standalone samples.
