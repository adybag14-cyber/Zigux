# Zigux Samples

This directory is the shared sample root for Zigux reference patterns and later runtime starter work.

Phase 5 reference samples
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Bytestream FIFO review packet
- keep `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `Documentation/zigux/phase5-kfifo-sample-survey.md` aligned through the shared `zigux/tests/phase5_build.zig` entrypoint
- keep the landed replay contract explicit: exact queue-order replay, transfer counts, wrapped replay-preview prefix, helper-side preview truncation, non-destructive snapshot, fixed embedded 32-byte ring-buffer backing, and the exact `checked_focus` order `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `reset_and_replay`, and `ownership_and_lifetime`
- keep the helper-only review surface explicit outside the main replay path: empty-queue null handling, the capacity ceiling, and queue-only reset remain part of the shipped contract
- keep procfs, `kfifo_from_user()` or `kfifo_to_user()`, locking, and runtime registration out of scope so this sample stays an approved Phase 5 in-memory FIFO idiom rather than a runtime module claim

Kobject review packet
- keep `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, and `Documentation/zigux/phase5-kobject-sample-survey.md` aligned through the shared `zigux/tests/phase5_build.zig` entrypoint
- keep the landed replay contract explicit: the static `kobject_example` directory cue, unnamed attribute-group shape, Linux `foo` or `baz` or `bar` attribute order, shared `0664` mode pattern, integer roundtrips, and the single `register_runs` ownership claim
- keep the ownership-and-lifetime review surface explicit outside the main replay path: the pre-registration zero-active-attributes boundary, initialized-only abandonment path, and post-exit rejection boundaries remain part of the shipped contract
- keep sysfs creation, `kernel_kobj` integration, uevents, and runtime registration out of scope so this sample stays a bounded in-memory ownership idiom rather than a runtime sysfs claim

Kretprobe review packet
- keep `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example_survey.zig`, and `Documentation/zigux/phase5-kretprobe-sample-survey.md` aligned through the shared `zigux/tests/phase5_build.zig` entrypoint
- keep the landed replay contract explicit: default symbol selection, pre-init retargeting, kernel-thread skip behavior, the single private entry timestamp, return-duration replay, the fixed `maxactive = 20` ceiling, and the bounded `nmissed` summary
- keep the ownership-and-lifetime review surface explicit outside the main replay path: timestamp-order rejection and recovery, armed-exit rejection, and post-exit handler rejection remain part of the shipped contract
- keep `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs` return extraction, and runtime module wiring out of scope so this sample stays a bounded non-runtime idiom rather than a Phase 9 starter claim

Trace-events review packet
- keep `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `Documentation/zigux/phase5-trace-events-sample-survey.md` aligned through the shared `zigux/tests/phase5_build.zig` entrypoint
- keep the landed replay contract explicit: selected-string slot and payload-length cues, the bounded array payload, the public main-iteration and callback-iteration cues, the `iter=%d` message, the `0xdeadbeef` bitmask word, the relative-location and vararg-payload path checks, exact event-family counts, the full modulo-selected string cycle, and the public lifecycle-summary plus `checked_focus` review surface
- keep the ownership-and-callback review surface explicit outside the main replay path: single-live callback registration, unregister-underflow rejection before a callback is armed, `OutstandingRegistration` rejection if `exit()` is attempted while one callback is still live, register-then-unregister balance, and post-exit replay or callback rejection remain part of the shipped contract
- keep `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and runtime registration out of scope so this sample stays a bounded in-memory approved payload-and-callback idiom rather than a Phase 9 runtime pilot claim

Later runtime starters, loader-side follow-ons, and blocked pilots
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events.zig` is still a sample-only blocked Phase 9 pilot on current `master`; there is no shipped `samples/zigux/runtime_trace_events_loader.zig` yet, so keep it separate from the loader-backed follow-ons above
- the runtime bitmap pair `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_loader.zig` stays a later Phase 9 runtime pilot packet rooted in `lib/test_bitmap.c`; keep it cataloged here as follow-on work rather than treating it as a fifth approved Phase 5 reference idiom

Review rules
- keep the four Phase 5 reference samples reviewable as bounded in-memory or non-runtime idiom readings
- do not treat the later `runtime_*` files in this directory as Phase 5 approved reference idioms
- keep the bitmap runtime pilot visibly separate from the approved Phase 5 idiom set: `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_loader.zig` belong with the Phase 9 runtime bitmap survey packet, not the four roadmap-approved Phase 5 anchor samples
- keep `samples/zigux/runtime_trace_events.zig` explicit as a sample-only blocked Phase 9 pilot until a real `samples/zigux/runtime_trace_events_loader.zig` lands, so the shared sample-root packet does not imply a fourth loader-backed runtime follow-on that current `master` does not ship
- keep sample-root notes aligned with `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`
- when `samples/zigux/kobject_example.zig`, `samples/zigux/kretprobe_example.zig`, or `samples/zigux/trace_events_sample.zig` changes, keep this sample-root catalog aligned with the focused replay test, manifest-backed survey, and sample-backed survey note instead of leaving the root-level contributor packet FIFO-only or partial
- current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample; keep string-helper evidence under the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, and `zigux/tests/phase7_build.zig`
- current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline evidence under the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig`

Focused local replays
- verify the bytestream FIFO sample directly: `zig test samples/zigux/bytestream_fifo.zig`
- verify the kobject sample directly: `zig test samples/zigux/kobject_example.zig`
- verify the kretprobe sample directly: `zig test samples/zigux/kretprobe_example.zig`
- verify the trace-events sample directly: `zig test samples/zigux/trace_events_sample.zig`
- verify the bytestream FIFO survey packet directly from the repo root: `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`
- verify the kobject survey packet directly from the repo root: `zig test zigux/tests/phase5_kobject_example_survey.zig`
- verify the kretprobe survey packet directly from the repo root: `zig test zigux/tests/phase5_kretprobe_example_survey.zig`
- verify the trace-events survey packet directly from the repo root: `zig test zigux/tests/phase5_trace_events_sample_survey.zig`

Helper-boundary checks
- verify the current approved Phase 5 reference sample inventory still resolves to the four roadmap anchors only: `find samples/zigux -maxdepth 1 -type f | sort | rg '/(bytestream_fifo|kobject_example|kretprobe_example|trace_events_sample)\.zig$'`
- verify the later `runtime_*` starters still stay cataloged separately from the approved Phase 5 anchors: `find samples/zigux -maxdepth 1 -type f | sort | rg '/runtime_.*\.zig$'`
- verify the runtime bitmap pair still stays cataloged as Phase 9 follow-on work rather than a fifth approved Phase 5 idiom: `rg -n "runtime_bitmap\.zig|runtime_bitmap_loader\.zig|Phase 9 runtime pilot packet|fifth approved Phase 5 reference idiom" samples/zigux/README.md`
- verify the trace-events runtime starter still stays sample-only with no shipped loader-side follow-on: `rg -n "runtime_trace_events\.zig|runtime_trace_events_loader\.zig|sample-only blocked Phase 9 pilot|no shipped \`samples/zigux/runtime_trace_events_loader.zig\` yet" samples/zigux/README.md`
- verify no Phase 5 string sample has appeared under this sample root: `find samples/zigux -maxdepth 1 -type f | sort | rg '/.*string.*\.zig$'`
- verify the shared docs still keep string-helper evidence in Phase 7 instead of `samples/zigux/`: `rg -n "samples/zigux/\\*string\\*|Phase 7 helper bundle|helper-only under \`lib/string_helpers.zig\`|phase7_string_helpers.zig|phase7_build.zig" Documentation/zigux/README.md Documentation/zigux/review-checklist.md Documentation/zigux/phase7-string-helpers-slice.md samples/zigux/README.md`
- verify no Phase 5 cmdline sample has appeared under this sample root: `find samples/zigux -maxdepth 1 -type f | sort | rg '/.*cmdline.*\.zig$'`
- verify the shared docs still keep cmdline evidence in Phase 7 instead of `samples/zigux/`: `rg -n "samples/zigux/\\*cmdline\\*|Phase 7 helper bundle|lib/cmdline.zig|phase7_cmdline.zig|phase7_build.zig" Documentation/zigux/README.md Documentation/zigux/review-checklist.md Documentation/zigux/phase7-cmdline-slice.md samples/zigux/README.md`
- verify the four shipped Phase 5 sample packets still pass together: `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
- verify the shipped string-helper and cmdline evidence still live under the separate Phase 7 helper bundle and shared build gate: `python3 scripts/zigux/validate-phase7.py`
