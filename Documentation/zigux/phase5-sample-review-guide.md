# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 lane reviewable without understating what current `master` already ships.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or one of the landed `samples/zigux/` reference-sample ports.

The roadmap-backed goal for Phase 5 is still narrow:

* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact replay routes visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-12 confirmed that current `master` still carries the bounded four-anchor Phase 5 packet together with its shared contributor surfaces, but the direct public-tree kobject evidence for this lane is still narrower than some older shared reminders implied.

Verified shared review surfaces on `master` are:
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

Verified landed Phase 5 sample packet surfaces on `master` are:
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_build.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_manifest.json`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kretprobe_example.zig`
* `zigux/tests/phase5_kretprobe_example_manifest.json`
* `zigux/tests/phase5_kretprobe_example_survey.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`
* `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
* `make -C zigux phase5-test`
* `make -C zigux phase5`

That same inspection also confirmed that the kobject anchor remains a narrower public-tree packet on current `master`: keep shared contributor wording aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, and keep `samples/zigux/kobject_example.zig` plus `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree gaps instead of claiming they are directly readable shipped evidence.

That same inspection also confirmed that later runtime-facing sample families are still present on `master`. Keep them under the separate Phase 9 lane instead of counting them as extra Phase 5 evidence:
* `samples/zigux/runtime_atomic64.zig`
* `samples/zigux/runtime_atomic64_loader.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_kretprobe.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_loader.zig`

Keep the workflow boundary explicit too: `.github/workflows/zigux-bootstrap.yml` reruns only `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, while `make -C zigux phase5-test` and `make -C zigux phase5` remain local Linux-style wrappers over that same shared build entrypoint.

## Review posture

Because the four approved Phase 5 anchors are already represented in the landed packet, same-lane follow-through should stay inside one of these bounded categories:

* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one shared-route or packet-alignment repair at a time
* one sample-local survey-note, manifest, or replay-contract update at a time when the coupled landed sample changes

Treat the current Phase 5 packet as landed but still intentionally non-runtime:
* the approved Phase 5 packet on current `master` is still the same four-anchor packet, but only three sample-root anchors are directly readable from `samples/zigux/`, while the kobject anchor remains reviewable through its narrower note-plus-focused-test-plus-manifest packet
* shared docs that describe those anchors, their paired test packets, and the shared `phase5_build.zig` route should stay aligned with that exact landed packet instead of reviving older pre-landing wording or overstating the current kobject readback surface
* local `make -C zigux phase5-test` and `make -C zigux phase5` routes should stay described as wrappers over the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay, not as a separate validation lane

Do not reopen sample behavior broadly, and do not count runtime-loader or runtime-pilot work as part of the non-runtime Phase 5 packet.

## Shared ownership map

When Phase 5 follow-through is doc-only, keep the shared-versus-sample-local split explicit so reminder-surface work does not reopen neighboring sample packets by accident.

* shared Phase 5 packet work belongs in `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` only when the change preserves the same four-sample non-runtime packet and the same shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay
* sample-local contract work belongs in exactly one landed packet at a time: the sample file under `samples/zigux/`, its paired survey note under `Documentation/zigux/`, the focused replay under `zigux/tests/phase5_*.zig`, the paired manifest, and the paired survey replay; for the current kobject anchor, keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` explicit together as the current readable kobject packet, and do not overclaim `samples/zigux/kobject_example.zig` or `zigux/tests/phase5_kobject_example_survey.zig` as shipped readback evidence until they are directly readable again
* if a shared doc needs to remind reviewers about one sample-specific ownership cue, point to the exact landed packet for that sample instead of re-describing behavior from memory or borrowing cues from a different sample family
* keep the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families out of shared Phase 5 reminder work unless the only purpose is to restate the already-landed Phase 5-versus-Phase 9 boundary
* when a sample-local contract moves, update the directly coupled sample packet first, then refresh the shared Phase 5 reminder surfaces only after those per-sample paths are directly readable on current `master`

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four approved anchors.

Keep these no-extra-sample reminders explicit too:
* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/cmdline.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting cmdline as a fifth Phase 5 sample
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep the approved formatting idiom cue bounded to the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 change, confirm:
* the roadmap anchor is one of the four approved Linux sample paths listed above
* the change says clearly whether it touches shared contributor guidance or one specific landed sample packet
* if a shared Phase 5 guide, README, checklist, survey note, manifest, test entrypoint, or make wrapper mentions a sample or replay route, that surface is directly readable on current `master`
* if a shared doc claims a sample-local survey note is part of the shipped packet, that exact survey note path is directly readable instead of being inferred from a sibling sample or older wording
* if a shared doc claims a sample-local replay route, the corresponding directly readable sample file, paired tests, paired manifest, and build entrypoint can all be read directly from the repo instead of being inferred from stale wording alone; for the current kobject anchor, keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` explicit together, and keep `samples/zigux/kobject_example.zig` plus `zigux/tests/phase5_kobject_example_survey.zig` out of shipped-readback claims until they are directly readable again
* if the shared packet mentions the non-runtime trace-events anchor, keep `samples/zigux/trace_events_sample.zig`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig` explicit together, and keep `ownershipSummary()` plus sample-owned `runOwnershipReplay()` explicit across that same shared reviewer packet instead of letting ownership-lifetime cues drift behind the payload, formatting, and callback helpers
* if a landed sample contract changes, the directly coupled survey note or manifest-backed contributor prompts move with it instead of lagging behind the sample code
* if shared guidance touches the landed `kretprobe` packet, keep sample-owned `runRetargetReplay()`, `runRecoveryReplay()`, `runOwnershipReplay()`, and `runLifecycleGuardReplay()` explicit across the guide, survey note, checklist, sample root, and any directly readable shared replay route, together with the fixed `maxactiveBudget()` cue at `20`, the outstanding-instance exit boundary, timestamp-order rejection and recovery, the one-missed-instance summary, and post-exit handler rejection
* the lane keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them
* later `runtime_*` sample and loader families remain clearly separated from the non-runtime Phase 5 packet

## Focused Sample Cues

### `trace_events_sample`

Review the landed trace-events packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` replay route.

Keep `formattedMessage()`, the selected-string plus `iter=%d` replay, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, the exact `checked_focus` order, restored registration balance, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, post-exit replay and callback-registration rejection, docs-root and sample-root contributor surfaces, and the Phase 5-versus-Phase 9 boundary explicit together as one bounded non-runtime packet.

Keep the no-extra-formatting reminder explicit too: no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample.

### `kretprobe_example`

Review the landed kretprobe packet through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`.

Keep `zigux/tests/phase5_kretprobe_example.zig` explicit as a focused replay wired through `zigux/tests/phase5_build.zig` rather than a standalone direct `zig test` entrypoint, while `zig test samples/zigux/kretprobe_example.zig` remains the sample-local direct self-check.

Keep `runRetargetReplay()`, `runRecoveryReplay()`, `runOwnershipReplay()`, and `runLifecycleGuardReplay()` explicit together with pre-init retargeting, the fixed `maxactiveBudget()` cue at `20`, the outstanding-instance exit boundary, timestamp-order rejection and recovery, the one-missed-instance summary, and post-exit handler rejection. Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference sample.

Keep `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` under their existing helper, rollback, and runtime lanes instead of treating bitmap as a shared Phase 5 approved idiom.

### `bytestream_fifo`

Review the landed bytestream FIFO packet through `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared `zigux/tests/phase5_build.zig` replay route.

Keep `StorageBacking.embedded_fixed_buffer`, `previewInto()`, `snapshotInto()`, the replay-visible preview markers `preview_len`, `preview_total_visible`, and `preview_truncated`, the short-drain `"hel"` plus queued `"lo"` helper boundary, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path explicit together as one bounded non-runtime packet. Do not describe extra queue-shape helper entrypoints here unless the sample itself, the paired bytestream tests, and the shared survey packet grow them together.

Keep the `reviewContract().focus` order explicit too: `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`.

### `kobject_example`

Review the current readable kobject packet through `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and the shared `zigux/tests/phase5_build.zig` replay route.

Keep the paired survey note, the focused replay, and the manifest explicit together as the current readable kobject packet on `master`, while shared reminders keep `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree gaps rather than shipped readback evidence.

Keep `runAnchorReplay()` explicit for the init-first, exact-three-attribute registration cue, `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary, `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward, `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch and parse-failure packet while the sample stays registered, `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` rejection packet, `ownershipSummary()` plus sample-owned `runOwnershipReplay()` explicit for the lifecycle packet, the unnamed attribute-group shape, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split together as one bounded non-runtime packet.

Keep `scripts/zigux/README.md` honest here too: the scripts-root Phase 5 summary may stay generic at the four-sample level, but it still needs to keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_build.zig` directly readable together as the exact current kobject packet beside the shared replay route instead of flattening this sample back to an unnamed summary or overstating the missing sample-root and survey paths.

## Non-goals

This shared Phase 5 guide does not claim:
* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure