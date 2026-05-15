# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-14 directly recovered these approved non-runtime Phase 5 sample-root files from current `master`:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`

Treat those four files as the current directly readable sample-root evidence for the roadmap-backed Phase 5 lane.

The roadmap-approved kobject anchor stays reviewable through this broader current packet too:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `samples/zigux/kobject_example.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kobject_example_survey.zig`
* `zigux/tests/phase5_build.zig`

Keep shared sample-root wording aligned with that mixed kobject packet: the survey note, sample, focused test, and manifest are directly readable here, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay current public-tree-backed companion evidence rather than direct authenticated-contents proof.

Keep the concrete kobject helper cues explicit in this shared sample-root reminder too: `runSingleInitBoundaryReplay()` keeps the one-time `init()` rule plus the zero-active-attributes `1/0/0` pre-registration state reviewable, `runPreRegistrationBoundaryReplay()` keeps initialized-but-not-registered `showValue()` and `storeValue()` rejection explicit, `runRegisteredBoundaryReplay()` keeps duplicate-registration plus registered-stage anchor-replay rejection and the bounded foo roundtrip explicit, `runInputValidationReplay()` keeps the shared `baz` and `bar` dispatch plus invalid-integer visibility explicit, `ownershipSummary()` plus `runOwnershipReplay()` keep the lifecycle counters and active-attribute snapshots explicit, and `runTeardownReplay()` keeps the registered teardown reset together with post-`exit()` show-or-store rejection and the `abandoned_before_registration` versus `tore_down_registered_attributes` split explicit.

The bytestream FIFO anchor is still directly readable at the sample root through `samples/zigux/bytestream_fifo.zig`, and the current bytestream packet now splits between that direct sample-root idiom, the directly readable manifest-backed companion path recorded in `Documentation/zigux/phase5-kfifo-sample-survey.md`, and the remaining public-tree-backed replay packet.

Fresh authenticated contents readback in this run now recovers this bytestream companion path too:

* `zigux/tests/phase5_bytestream_fifo_manifest.json`

Authenticated contents readback in this run still did not recover these remaining bytestream companion paths:

* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`
* `zigux/tests/phase5_build.zig`

But the sibling bytestream survey note already records current public-tree blob readback for those remaining files, so shared contributor guidance here should keep that split explicit instead of flattening the bytestream anchor back to sample-plus-note only or claiming the authenticated route already recovered the whole packet.

Keep contributor guidance here aligned with `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, the directly readable bytestream manifest companion `zigux/tests/phase5_bytestream_fifo_manifest.json`, and the remaining public-tree-backed bytestream replay packet, including the direct `runRemainingCapacityReplay()`, `occupancySummary()`, and `writableSpanSummary()` helper cues now visible in the sample file, while still saying clearly that authenticated contents readback for the focused tests-root replay and shared-build paths remains flaky in this environment.

The kretprobe anchor is also directly reviewable again through this bounded packet:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `samples/zigux/kretprobe_example.zig`
* `zigux/tests/phase5_kretprobe_example.zig`
* `zigux/tests/phase5_kretprobe_example_manifest.json`
* `zigux/tests/phase5_kretprobe_example_survey.zig`

Keep shared sample-root wording aligned with that directly readable kretprobe packet, including the restored non-runtime `kernel_clone` default, `runRetargetReplay()`, `runAnchorReplay()`, `runLifecycleGuardReplay()`, `runOwnershipReplay()`, and `runRecoveryReplay()` cues, but do not restate the missing shared `zigux/tests/phase5_build.zig` route as direct readback evidence until it returns.

The trace-events anchor is also directly reviewable again through this bounded packet:

* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`

Keep shared sample-root wording aligned with that directly readable trace-events packet, including the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`, but do not restate the missing shared `zigux/tests/phase5_build.zig` route as direct readback evidence until that path returns.

## Separate Phase 9 runtime pilot family

Keep later runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence.

* keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` as the shared owner map for the runtime-loader lane versus the pilot-family packets
* keep older command and environment control boundaries under the existing tooling lanes instead of reading the runtime loader packet as shipped command or environment activation control
* if a proposed sample needs runtime-loader wiring, scheduler-visible execution, workqueue handoff, ring-buffer substrate, or other live kernel execution context to make its contract honest, route it to the separate runtime lane instead of widening Phase 5

Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep direct bitmap helper reviewability in its existing helper and runtime lanes instead of counting runtime-facing bitmap work as a fifth approved Phase 5 sample idiom.

## Approved Phase 5 sample scope

The roadmap-backed Phase 5 sample anchors are still limited to these four Linux sample paths:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Those anchors remain the approved Phase 5 target set.

On current `master`, shared contributor guidance from this directory should keep the four directly readable sample-root files `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, `samples/zigux/kretprobe_example.zig`, and `samples/zigux/trace_events_sample.zig` explicit, keep the bytestream anchor aligned with `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, the directly readable `zigux/tests/phase5_bytestream_fifo_manifest.json`, and the remaining public-tree-backed bytestream companion packet `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig` while still keeping the authenticated-contents-readback gap for those remaining broader bytestream paths explicit, keep the kobject anchor aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and the current public-tree-backed companion packet `zigux/tests/phase5_kobject_example_survey.zig` plus `zigux/tests/phase5_build.zig`, keep the kretprobe anchor aligned with `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` while keeping the shared `zigux/tests/phase5_build.zig` route explicit as the current shared readback gap, and keep the trace-events anchor aligned with `Documentation/zigux/phase5-trace-events-sample-survey.md`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`.

## Contributor guidance

When touching Phase 5 contributor guidance:

* keep roadmap scope narrow to the four approved anchors above
* treat `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, `samples/zigux/kretprobe_example.zig`, and `samples/zigux/trace_events_sample.zig` as the current directly readable sample-root evidence from this directory
* keep the kobject anchor aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and the current public-tree-backed companion packet `zigux/tests/phase5_kobject_example_survey.zig` plus `zigux/tests/phase5_build.zig`, keep `runSingleInitBoundaryReplay()` explicit for the one-time `init()` rule plus the zero-active-attributes `1/0/0` pre-registration state, `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered `showValue()` and `storeValue()` rejection boundary, `runRegisteredBoundaryReplay()` explicit for duplicate-registration plus registered-stage anchor-replay rejection and the bounded foo roundtrip afterward, `runInputValidationReplay()` explicit for the shared `baz` and `bar` dispatch plus invalid-integer visibility while the sample stays registered, `ownershipSummary()` plus `runOwnershipReplay()` explicit for lifecycle counters and active-attribute snapshots, `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` show-or-store rejection, and keep `zigux/tests/phase5_kobject_example_survey.zig` plus `zigux/tests/phase5_build.zig` framed as current public-tree-backed companion evidence rather than direct authenticated-contents proof
* keep the bytestream anchor aligned with `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, the directly readable manifest companion `zigux/tests/phase5_bytestream_fifo_manifest.json`, and the remaining public-tree-backed bytestream replay packet `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig`, keep `StorageBacking.embedded_fixed_buffer`, `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `runRemainingCapacityReplay()`, the short-drain `"hel"` plus queued `"lo"` helper boundary, the direct empty/full and queue-window helpers `available()`, `occupancySummary()`, `visibleSpanSummary()`, `writableSpanSummary()`, and `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle explicit, and keep the authenticated-contents-readback gap for the remaining replay and shared-build companion paths explicit instead of describing the whole anchor as sample-only again or claiming the authenticated route already recovered the entire packet
* keep the kretprobe anchor aligned with `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, keep the restored non-runtime `kernel_clone` default plus the `runRetargetReplay()`, `runAnchorReplay()`, `runLifecycleGuardReplay()`, `runOwnershipReplay()`, and `runRecoveryReplay()` cues explicit, and do not claim `zigux/tests/phase5_build.zig` as direct evidence until a fresh reread proves it returned
* keep the trace-events anchor aligned with `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`, keep the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` explicit, and do not claim `zigux/tests/phase5_build.zig` as direct evidence until a fresh reread proves it returned
* do not treat review notes by themselves as proof of additional current sample files beyond the direct readback recovered in this run
* keep runtime-facing `runtime_*` work in the separate later runtime lane instead of folding it into Phase 5
* keep direct `bitmap` helper reviewability in its existing helper or runtime lanes instead of implying an extra Phase 5 sample

## Phase 7 no-sample boundaries

* current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, and keep the ownership-focus packet visible there too: first-NUL trimming and prefix skipping stop at the exported C-string boundary, exact-fit, terminator-only, and zero-capacity unescape destinations stay caller-owned, append-limited escape accounting stays inside caller storage, `kasprintfStrarray()` and `kfreeStrarray()` keep per-string allocations, the NULL-terminated pointer view, the shared zero-length sentinel, and teardown ownership explicit for caller-held results, and `memcpyAndPad()` plus `strreplace()` stay bounded by caller-provided destinations; treat any new `samples/zigux/*string*.zig` file as review-blocking unless the roadmap lane is explicitly reopened
* current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`
* current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`
* current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Boundary notes

Respect the freeze map here too.

* do not add Phase 5 follow-ons derived from freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
* keep the study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` families out of this directory until a later roadmap-backed lane explicitly reopens that boundary
* if a proposed sample needs runtime-loader wiring, scheduler-visible execution, workqueue handoff, ring-buffer substrate, or other live kernel execution context to make its contract honest, route it to the separate runtime lane instead of widening Phase 5

## Review pointers

For shared Phase 5 guidance, use:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Use those shared surfaces to keep roadmap scope, contributor wording, the directly readable bytestream, kobject, kretprobe, and trace-events sample-root evidence, the current kobject packet with directly readable sample or test evidence plus the public-tree-backed survey-and-build companions, the directly readable kretprobe packet, the directly readable trace-events packet, and the Phase 5-versus-runtime boundary honest.