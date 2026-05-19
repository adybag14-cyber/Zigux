# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-19 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

The authenticated contents route used for this lane reconfirmed the direct bytestream, kobject, kretprobe, trace-events formatting-companion, and runtime trace-events entries above. Fresh public-tree readback also reconfirmed the directly coupled kobject focused test and manifest, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence in this runtime.

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` keeps the bytestream sample-root port directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`.
Current `master` keeps the kobject sample-root port directly readable in `samples/zigux/` through `samples/zigux/kobject_example.zig`.
Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.
For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly. Keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence rather than direct authenticated proof.

Keep the kobject anchor framed as a roadmap-backed Phase 5 target with a mixed direct-plus-public-tree-backed packet: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread returns them directly too. Keep shared contributor guidance honest about that split-readback packet instead of repeating the older kobject-reread-needed sample-root wording or overstating fully direct authenticated proof.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream anchor, treat `samples/zigux/bytestream_fifo.zig` as the current direct sample-root proof for the roadmap-backed non-runtime lane.
Keep `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as directly readable paired test evidence when the bytestream packet needs a primary replay witness.
Keep `zigux/tests/phase5_bytestream_fifo_manifest.json` explicit as directly readable manifest evidence for the current bytestream packet.
Keep `Documentation/zigux/phase5-kfifo-sample-survey.md` explicit as the current direct bytestream survey proof beside `samples/zigux/bytestream_fifo.zig`, and keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence or repo-reality-gap surfaces until a fresh reread proves direct authenticated proof again.

When a shared Phase 5 guide, checklist, or README mentions the kobject anchor, keep the roadmap-backed non-runtime lane explicit while treating `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` as directly readable packet evidence again, and keep `zigux/tests/phase5_kobject_example_survey.zig` plus `zigux/tests/phase5_build.zig` explicit as current public-tree-backed companion evidence until a fresh reread proves direct authenticated proof for those two routes again.
Keep the landed `samples/kobject/kobject-example.c` packet reviewable as the approved in-memory ownership-and-lifetime idiom rather than as runtime parity.
Keep `phase5-kobject-sample-survey.md` and `phase5_kobject_example_survey.zig` explicit in that same reminder packet.
Keep `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes boundary.
Keep `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit as the reviewable lifecycle cues.
Keep `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch plus parse-failure visibility.
Keep the initialized-only abandonment cue explicit beside the `abandoned_before_registration` exit split.
Keep the already-registered duplicate-registration and replay-restart rejection packet explicit beside the bounded foo roundtrip.
Keep the registered teardown reset and post-`exit()` show-or-store rejection explicit beside the `tore_down_registered_attributes` exit split.

When a shared Phase 5 guide, checklist, or README mentions the kretprobe anchor, treat `samples/zigux/kretprobe_example.zig` as the current direct sample-root proof for the roadmap-backed non-runtime lane.
Keep `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit as directly readable paired test evidence for the restored non-runtime kretprobe packet.
For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit in the same reminder packet. Keep the bounded formatting companion as the current direct cue for the approved non-runtime trace-events anchor, keep it framed as a sibling cue instead of a fifth sample, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route framed as public-tree-backed companion, repo-reality-gap, or historical-support references rather than direct authenticated proof.

Keep `samples/zigux/trace_events_string_formatting_sample.zig` tied to the same non-runtime trace-events anchor as a bounded formatting companion.
Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.

Keep the shared `zigux/tests/phase5_build.zig` route in companion-evidence wording only when a fresh reread confirms that path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Phase 9 runtime pilot family

The surviving direct runtime-module sample packet in this directory is centered on `samples/zigux/runtime_trace_events.zig`.
Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `zigux/tests/README.md` aligned with that surviving direct runtime-module sample instead of reviving the removed shared loader packet by implication.

Keep the current direct runtime-module evidence explicit here too: `samples/zigux/runtime_trace_events.zig` still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking, so the separate runtime lane still has one shipped selftest-hook and lifecycle-parity sample-root proof on current `master`. The same direct sample now also keeps initialized-stage clean exit explicit through `test "trace-events sample preserves initialized summary across direct exit without selftest"`, which proves zero selftest runs stay explicit, the initialized summary stays unchanged until `exit()` succeeds, and later lifecycle calls remain rejected without drift.

Keep the companion boundaries explicit here too: `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps the same narrow packet's unregistered function-thread failures fail-closed, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` keeps failed-exit rollback explicit after reusable selftest replay by proving `error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread unregisters and then keeps post-exit invalid-lifecycle rejections fail-closed too, while `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps balanced function-thread registration reusable before and after selftest, including the later selftest_complete duplicate-registration rejection that leaves the summary unchanged before the reusable replay continues.

Keep the returned family-local `zigux/tests/runtime_*` witness explicit here too: `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` keep the same narrow trace-events packet reviewable under `zigux/tests/runtime_*` without promoting that witness into evidence that the broader shared runtime-loader family returned.

Fresh public-tree reread on 2026-05-19 also reconfirmed the separate runtime bitmap family on current `master`: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_manifest.json`, and `Documentation/zigux/phase9-runtime-bitmap-survey.md`. Keep that returned bitmap packet framed as a separate Phase 9 runtime family rather than as directly readable neighboring proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here. Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` companion stays bitmap-local even though the wider runtime substrate is still blocked. Keep any `phase9-*` Makefile route names framed as absent backlog vocabulary unless a fresh repo reread proves they have returned on current `master`.

Keep saying clearly that current `master` does not currently expose the broader shared runtime-loader packet. Current `master` now does return `zigux/tests/phase9_build.zig` again, but as a bounded Phase 9 build bundle whose live body names `zigux/tests/runtime_atomic64_diff.zig`, the separate runtime bitmap sample/module/diff/loader/survey/top-bit targets, and a shared build-handle route that pairs `samples/zigux/runtime_bitmap_loader.zig` with the still-missing `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`; the broader shared `zigux/tests/runtime_*` replay family beyond the returned trace-events survey witness, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the older broader shared `samples/zigux/runtime_*_loader.zig` scaffolds stay backlog references unless a fresh repo reread proves they have returned. Keep `zigux/Makefile` named only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes, and keep `.github/workflows/zigux-bootstrap.yml` named only as a shared repo-level workflow surface, not as dedicated Phase 9 evidence.

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

Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; cmdline reviewability remains under `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_cmdline_survey.zig` rather than the four shipped Phase 5 samples.

Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, bitmap, `printf`, `vsprintf`, or broad `format` sample families landed here as standalone samples.