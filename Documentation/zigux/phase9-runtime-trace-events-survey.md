# Phase 9 Runtime Trace-Events Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/trace_events/trace-events-sample.c`.

## Status

- `PHASE9_STATUS=parked`
- `PHASE9_SLICE=runtime-trace-events-survey`
- `PHASE9_LANE_KEY=P9-L12`
- `PHASE9_SURVEYED_COMMIT=d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`
- scope: survey manifest, starter sample, bounded loader scaffold, dedicated module and survey gates, shared Phase 9 build wiring, and the lane-level review note that now tracks the landed starter plus its shipped selftest hook, lifecycle parity evidence, and machine-checkable diagnostics summary with explicit per-thread event totals plus explicit replay run counters without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_trace_events.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_trace_events_diff.zig`
  - `zigux/tests/runtime_trace_events_module.zig`
  - `zigux/tests/runtime_trace_events_manifest.json`
  - `zigux/tests/runtime_trace_events_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-trace-events-survey.md`
  - `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/trace_events/trace-events-sample.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally had no matching trace-events survey artifact, no dedicated `runtime_*` review gate, and no Zigux starter under `samples/zigux/`. That survey note now stays in place as the lane history and review anchor after the bounded starter sample, the blocked loader scaffold, and the focused module tests landed, so Phase 9 can keep recording what is shipped versus what still depends on the runtime substrate.

The roadmap and the freeze map also keep an adjacent trace substrate boundary explicit: `kernel/trace/ring_buffer.c` remains `Study / Boundary Only` in `Documentation/zigux/freeze-map.md`. That means this lane may ship a bounded trace-events starter, a blocked loader scaffold, and survey evidence, but it must not imply ring-buffer parity, deep trace transport ownership, or any Architecture Council-approved status change for the frozen trace core.

The same governance packet also treats `Documentation/zigux/review-checklist.md` as the review-side owner for the trace-core freeze-boundary prompt, so the `Study / Boundary Only` posture stays explicit in the review checklist beside the survey note, manifest, and freeze map instead of living only in one document.

No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 lane. The evidence here is limited to keeping the study-only blocker explicit until a separate governance packet reopens that anchor.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` at 153 lines.
- the current survey packet is pinned to `master` commit `d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`.
- `samples/trace_events/trace-events-sample.h` is present on `master` at 640 lines.
- the manifest-backed review packet now keeps `samples/trace_events/trace-events-sample.h` explicit as a header-side macro boundary with a 640-line surveyed boundary, so the parked trace-events lane can point at the real header surface without turning it into a generated tracepoint macro parity claim.
- the Linux ftrace selftests already reference `trace-events-sample` as a modprobe and event-enabling target in at least two places.
- the repo had zero `zigux/tests/runtime_trace_events*` files before this survey landed.
- the repo now carries `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, `zigux/tests/runtime_trace_events_diff.zig`, the survey manifest and gate, and shared `zigux/tests/phase9_build.zig` coverage for the trace-events starter lane.
- the current bounded starter now records concrete main-thread payload literals for `foo_bar`, template, conditional, template-print, and relative-location replay paths, plus explicit function-callback payload labels and the exported `iter=%d` format template.
- the current bounded starter also exposes a stable `RuntimeTraceEventsSummary` view for stage, registration depth, iteration counts, explicit main-thread and function-thread event totals, explicit `foo_bar_reg` and `foo_bar_unreg` registration labels, `init_runs`, `selftest_runs`, and `exit_runs`, payload-presence flags, and the latest bounded main-thread and function-thread payload literals so logging diagnostics stay machine-checkable.
- the main-thread replay now also keeps the Linux sample's `count % 5` array-shape replay explicit through the summary surface by recording the bounded vararg array length and its zero terminator alongside the selected random string.
- the current replay contract now keeps the count-gated conditional paths explicit too: direct `emitMainIteration(7)` leaves both conditional messages absent, while the count-zero selftest path still records both conditional families and the later mixed replay keeps the combined `10` main-thread, `4` function-thread, and `14` total-event summary counts machine-checkable after direct pilot activity.
- the starter now makes the roadmap's shipped selftest hook explicit through `provides_selftest_hook = true` on the bounded descriptor surface.
- the focused module, sample, and diff gates now prove the bounded replay counts, explicit per-thread event totals, replay run counters, payload literals, and failed-exit rollback proof through the summary surface, so the stable diagnostics view stays aligned with the concrete Linux-sample replay paths instead of drifting behind raw field access.
- the same focused module and sample gates now also keep the selftest-ready failed-exit rollback explicit: after the shipped selftest path, a rejected exit with one outstanding registration preserves the explicit `10` main-thread, `4` function-thread, and `14` total-event summary plus the latest payload literals until unregister and exit complete normally.
- the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold now keeps the review-only `foo_bar_reg` and `foo_bar_unreg` labels, explicit `waiting_on_runtime_substrate` to `released_without_substrate` fallback, and pre-execution loader shape visible without claiming any shared runtime-loader binding or executable runtime substrate.
- the manifest-backed review packet now also records an explicit sample path, the shared Phase 9 validation entrypoint, review prompts, a delivery_evidence_catalog, an ownership_map, exact checks, and non-goals so reviewers can tell which parts of the starter, blocked loader scaffold, paired module-slice note, review checklist, and freeze-boundary packet are shipped contract versus still-blocked runtime substrate.
- the review-side freeze-boundary packet also now keeps `Documentation/zigux/review-checklist.md` explicit beside `Documentation/zigux/freeze-map.md`, so the trace-core study boundary is carried by both the lane note and the shared review prompts instead of being implied through the freeze map alone.
- the shared `zigux/tests/phase9_build.zig` bundle still avoids any trace-events loader test target, so the trace-events loader scaffold remains a loader-free blocker inside the shared build packet while runtime task ownership, polling and event-loop substrate, thread creation, and tracepoint-registration lifecycle wiring remain blocked.
- the paired module-slice note now repeats that blocked loader-scaffold handoff explicitly so the dedicated docs cannot drift into implying a shared loader target or scheduler-facing substrate before the shared runtime handoff exists.
- the same lane also stays under the freeze-map study boundary for `kernel/trace/ring_buffer.c`, so the shipped survey evidence must keep ring-buffer parity, trace transport ownership, and any freeze-map status change out of scope until the Architecture Council explicitly reopens that anchor.
- no parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 lane, so the current trace-events packet remains a study-boundary note rather than a freeze-map reopen request.

## Delivery ownership map

The manifest-backed delivery packet now names which surface owns each part of the shipped Phase 9 trace-events review bundle:

- `samples/zigux/runtime_trace_events.zig` owns the bounded trace-events starter descriptor, lifecycle surface, diagnostics summary, and shipped selftest hook
- `samples/zigux/runtime_trace_events_loader.zig` owns the bounded loader-plan scaffold, review-only register/unregister labels, and the explicit release-without-substrate fallback while shared runtime-substrate ownership stays blocked
- `zigux/tests/runtime_trace_events_module.zig` owns the dedicated lifecycle, summary-surface, registration-label, conditional-replay, and failed-exit rollback checks for the starter
- `zigux/tests/runtime_trace_events_diff.zig` owns the bounded payload and function-callback replay checks against the Linux sample anchor
- `zigux/tests/runtime_trace_events_survey.zig` owns the machine-checkable replay of the manifest, review prompts, exact checks, loader-free blocker, and freeze-map boundary
- `zigux/tests/runtime_trace_events_manifest.json` owns the manifest-backed delivery catalog, ownership map, exact checks, and non-goal packet for this slice
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 runtime bundle entrypoint for the trace-events starter while the trace-events loader target stays absent
- `Documentation/zigux/phase9-runtime-trace-events-survey.md` owns the lane history, recorded gaps, delivery ownership map, and bounded blocker posture for the survey packet
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md` owns the landed starter surface summary, direct sample and diff gate posture, the blocked loader-scaffold restatement, and the paired header-side macro boundary note for `samples/trace_events/trace-events-sample.h`
- `Documentation/zigux/review-checklist.md` owns the shared review prompt that keeps the `kernel/trace/ring_buffer.c` study boundary, the no-status-change posture, and the Architecture Council reopen rule explicit during review
- `Documentation/zigux/freeze-map.md` owns the study-only `kernel/trace/ring_buffer.c` boundary and the Architecture Council reopen rule for trace-core status changes

## Recorded gaps

The manifest started as a survey-only inventory and now records:

- the manifest-backed `runtime-trace-events-delivery-catalog`
- the manifest-backed `runtime-trace-events-ownership-map`
- the landed `phase9-build-gate`
- the landed `runtime-trace-events-survey-gate`
- the landed `runtime-trace-events-sample-module` starter
- the landed `runtime-trace-events-loader-scaffold`
- the landed `runtime-trace-events-module-tests`
- the landed `runtime-trace-events-diff-gate`
- the blocked `runtime-trace-events-freeze-map-boundary`
- the still-blocked runtime substrate handoff
- review prompts that keep the bounded summary surface, loader-free blocker, and freeze-map boundary explicit
- review prompts that keep the `samples/trace_events/trace-events-sample.h` header-side macro boundary explicit without implying generated tracepoint macro parity
- exact checks for the descriptor contract, diagnostics summary, main-thread payload replay, function-callback registration balance, selftest family order, failed-exit rollback, the header-side macro boundary, governance boundary, and the blocked loader scaffold inside the shared build packet
- non-goals that keep loadable-module, event-loop, ring-buffer, macro-generation, and full selftest parity claims out of scope

This keeps the survey useful after the first starter slice lands without pretending that Zigux already has a loadable trace-events runtime module.

## Gates

1. run the focused trace-events survey replays
- `zig test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig`
- `make -C zigux phase9-trace-events-survey`
- the standalone replay keeps the dedicated trace-events survey packet reviewable with the shipped sample import, and the make target wraps that same focused survey gate without implying a loader path while the trace-core freeze boundary stays study-only

2. run the shared Phase 9 runtime packet replay
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- this shared build now includes `phase9-runtime-trace-events-sample-tests`, `phase9-runtime-trace-events-module-tests`, `phase9-runtime-trace-events-diff-tests`, and `phase9-runtime-trace-events-survey-tests` so the starter, diff, and survey evidence stay explicit in one shared packet while `phase9-runtime-trace-events-loader-tests` remains absent

3. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux trace-events runtime module
- runtime task ownership or event-loop substrate parity
- polling-backed wake or dispatch behavior
- runtime trace registration or unregister parity with the Linux sample
- parity or ownership for `kernel/trace/ring_buffer.c`
- any freeze-map status change for the trace core without an Architecture Council decision
- generated tracepoint macro parity for `trace-events-sample.h`
- full ftrace selftest execution inside Zigux

## Next bounded step

Keep the shipped Phase 9 runtime trace-events starter parked. Reopen this lane only for a later small runtime-substrate handoff around module entry, shared runtime-loader binding, runtime task ownership, polling and event-loop substrate, thread creation, or tracepoint-registration lifecycle wiring, while keeping the separate `kernel/trace/ring_buffer.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it.
