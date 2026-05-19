# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-19 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

The authenticated contents route used for this lane reconfirmed the direct bytestream, kretprobe, trace-events formatting-companion, and runtime trace-events entries above. Earlier reminder surfaces still mention the older kobject sample-root route, but that path still needs a fresh reread before this README can treat it as current direct sample-root evidence.

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` keeps the bytestream sample-root port directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`.
Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.
For the trace-events anchor, keep shared contributor guidance grounded in the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet. Fresh authenticated reread on 2026-05-19 still directly reconfirmed that bounded formatting companion, while the broader non-runtime trace-events sample-local companions still need a fresh reread before this README can treat them as returned current-`master` evidence:

* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`

Keep the kobject anchor framed as a roadmap-backed Phase 5 target plus shared-reminder, current public-tree-backed companion, or repo-reality-gap surface rather than as current direct sample-root proof.
Keep shared contributor guidance honest about that split-readback packet instead of repeating the older broader trace-events wording or overstating direct authenticated proof.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream anchor, treat `samples/zigux/bytestream_fifo.zig` as the current direct sample-root proof for the roadmap-backed non-runtime lane.
Keep `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as directly readable paired test evidence when the bytestream packet needs a primary replay witness.
Keep `zigux/tests/phase5_bytestream_fifo_manifest.json` explicit as directly readable manifest evidence for the current bytestream packet.
Keep `Documentation/zigux/phase5-kfifo-sample-survey.md` explicit as the current direct bytestream survey proof beside `samples/zigux/bytestream_fifo.zig`, and keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence or repo-reality-gap surfaces until a fresh reread proves direct authenticated proof again.
When a shared Phase 5 guide, checklist, or README mentions the kobject anchor, keep the roadmap-backed non-runtime lane explicit while treating `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, and `zigux/tests/phase5_build.zig` only as current public-tree-backed companion evidence or repo-reality-gap surfaces until a fresh reread proves direct authenticated-contents proof again.
When a shared Phase 5 guide, checklist, or README mentions the kretprobe anchor, treat `samples/zigux/kretprobe_example.zig` as the current direct sample-root proof for the roadmap-backed non-runtime lane.
Keep `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit as directly readable paired test evidence for the restored non-runtime kretprobe packet.
For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and the shared `zigux/tests/phase5_build.zig` route explicit in the same reminder packet. Keep the bounded formatting companion as the direct authenticated proof, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap or shared-reminder surfaces until a fresh reread proves they returned directly on current `master`.

Keep `samples/zigux/trace_events_string_formatting_sample.zig` tied to the same non-runtime trace-events anchor as a bounded formatting companion.
Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.

Keep the shared `zigux/tests/phase5_build.zig` route in companion-evidence wording only when a fresh reread confirms that path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Phase 9 runtime pilot family

The surviving direct runtime-module sample packet in this directory is centered on `samples/zigux/runtime_trace_events.zig`.
Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `zigux/tests/README.md` aligned with that surviving direct runtime-module sample instead of reviving the removed shared loader packet by implication.

Keep the current direct runtime-module evidence explicit here too: `samples/zigux/runtime_trace_events.zig` still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking, so the separate runtime lane still has one shipped selftest-hook and lifecycle-parity sample-root proof on current `master`.

Keep the companion boundaries explicit here too: `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps the same narrow packet's unregistered function-thread failures fail-closed, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` keeps failed-exit rollback explicit after reusable selftest replay by proving `error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread unregisters and then keeps post-exit invalid-lifecycle rejections fail-closed too, while `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps balanced function-thread registration reusable before and after selftest, including the later selftest_complete duplicate-registration rejection that leaves the summary unchanged before the reusable replay continues.

Keep the returned family-local `zigux/tests/runtime_*` witness explicit here too: `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` keep the same narrow trace-events packet reviewable under `zigux/tests/runtime_*` without promoting that witness into evidence that the broader shared runtime-loader family returned.

Keep saying clearly that current `master` does not currently expose the broader shared runtime-loader packet, so `zigux/tests/phase9_build.zig`, the broader shared `zigux/tests/runtime_*` replay family beyond that returned narrow survey witness, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds stay backlog references unless a fresh repo reread proves they have returned; keep `zigux/Makefile` named only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes, and keep `.github/workflows/zigux-bootstrap.yml` named only as a shared repo-level workflow surface, not as dedicated Phase 9 evidence.

Keep older cross-phase non-owner boundaries explicit: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.

Treat `samples/zigux/runtime_trace_events_unregistered_gate.zig` as the same narrow runtime packet's fail-closed companion for unregistered function-thread failures and post-exit invalid-lifecycle rejections, including the initialized-before/after, selftest_complete-before/after, and exited-before/after summary-stability checks, treat `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` as the same narrow runtime packet's failed-exit rollback companion, including the selftest_complete-before/after, before-exit/after-exit, and exited-before/after summary-stability checks around `error.OutstandingRegistration` plus the later post-exit invalid-lifecycle rejections, and treat `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` as the same packet's balanced registration re-entry companion across the initialized and selftest_complete stages, not as proof that the broader shared loader family has returned.

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

Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, bitmap, `printf`, `vsprintf`, or broad `format` sample families landed here as standalone samples.
