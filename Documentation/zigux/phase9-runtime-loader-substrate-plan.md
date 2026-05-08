# Phase 9 Shared Runtime Loader Substrate Plan

This document captures the bounded Phase 9 follow-up after the landed atomic64, bitmap, kretprobe, and trace-events loader scaffolds. It records the first shared request surface already used by the atomic64, bitmap, and kretprobe loaders while keeping the trace-events scaffold parked at the blocked sample-only boundary.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=shared-runtime-loader-substrate-plan`
- `PHASE9_LANE_KEY=P9-L16`
- scope: shared request shape, shared loader-stage vocabulary, allocator-handoff and command-name review surfaces, atomic64 plus bitmap plus kretprobe handoff alignment, the landed trace-events blocked-scaffold boundary, and an explicit low-risk path that now lands as `zigux/kernel/runtime_loader.zig` without claiming live runtime execution
- product boundary:
  - `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The live repo already ships four bounded loader-handoff surfaces:

- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`

The first three files currently stop at the same honest blocker: they can prepare a reviewable handoff plan, request runtime loading, and release without substrate, but they still have nowhere shared to send that handoff inside Zigux. The trace-events scaffold is now landed too, but it remains intentionally sample-only while the shared loader packet keeps the trace core at a study-only freeze boundary.

That makes the next useful step a shared substrate surface rather than another lane-local wording pass or a premature runtime-module implementation. This note therefore stays tied to the live shared loader packet on current `master` instead of a removed dedicated validator stack.

## Shared facts already visible in the repo

The landed atomic64, bitmap, and kretprobe loaders already agree on several core ideas:

- a loader begins at `idle`, moves to `prepared`, then to `waiting_on_runtime_substrate`, and can fall back to `released_without_substrate`
- each lane exposes a bounded handoff plan rather than pretending the runtime substrate already exists
- each plan carries module identity, Linux anchor provenance, explicit init and exit symbol names, and the current sample lifecycle stage
- each lane keeps `requires_runtime_substrate` and `provides_selftest_hook` explicit instead of hiding them in prose
- each lane can keep an optional shared `command_name` handoff reviewable without claiming broader argv-policy or environment-derived activation control
- each lane now relies on an explicit allocator handoff derived from `zigux/helpers/allocator_policy.zig` instead of leaving allocator ownership implicit in lane-local notes

The main differences are lane-specific payload details:

- atomic64 needs a bounded counter snapshot plus `init_runs`, `selftest_runs`, and `exit_runs` reviewability
- bitmap needs a bounded bitmap summary that can seed first-set, first-zero, weight, and bit-count review
- kretprobe needs explicit `register_kretprobe` and `unregister_kretprobe` naming plus symbol, `maxactive`, and private-data-size handoff facts

## Landed first shared substrate

The first shared code step stayed intentionally small:

1. add `zigux/kernel/runtime_loader.zig` as a pure data-and-state surface only
2. define one shared stage enum for the loader handoff lifecycle
3. define one shared request struct for the common module identity and lifecycle facts
4. carry lane-specific details in a narrow tagged payload rather than separate unrelated loader state machines
5. keep every path testable through `zigux/tests/phase9_build.zig` without introducing real kernel loader hooks

The landed shared request keeps these common fields explicit:

- module name
- optional shared `command_name` handoff field
- Linux anchor path
- entry symbol
- exit symbol
- `requires_runtime_substrate`
- `provides_selftest_hook`
- sample handoff stage
- explicit `allocator_handoff` facts derived from `zigux/helpers/allocator_policy.zig`
- lane kind such as atomic64, bitmap, or kretprobe

The first lane payloads stay small:

- atomic64 payload: counter snapshot plus lifecycle counters only
- bitmap payload: summary snapshot only
- kretprobe payload: register API, unregister API, symbol name, `maxactive`, private-data bytes, and current bookkeeping summary

## Current acceptance boundary

The first shared substrate implementation is now ready because:

- atomic64, bitmap, and kretprobe can all export a common request shape without losing their current lane-specific facts
- the shared Phase 9 build can run focused tests for that common request shape
- the code still makes it impossible to confuse a bounded handoff with a real loadable runtime module
- the trace-events lane remains free to adopt the same request shape later without forcing the first implementation to solve thread creation or tracepoint registration
- the shared request keeps `command_name` reviewable as a narrow handoff clue that can later mirror `ExtractArgv0Result.command_name` without claiming a finished argv or environment control plane
- allocator ownership now stays machine-checkable through the shared `allocator_handoff` record before any real runtime loader exists

That still leaves the broader control plane blocked.

Any future non-null `command_name` must keep a truthful Phase 8 owner such as `tools/lib/subcmd/exec-cmd.zig` and `ExtractArgv0Result.command_name`, and this slice still does not claim `Config.exec_path_env`, `PERF_EXEC_PATH`, `PATH`, or other environment-derived activation handling as runtime-loader behavior.

## Adjacent freeze boundaries

The shared request surface also stays parked beneath the nearby freeze-map boundaries:

- `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this substrate note must not imply scheduler transport ownership, polling, event-loop behavior, or workqueue-parity progress.
- `samples/zigux/runtime_trace_events.zig` remains the fourth Phase 9 pilot, and its bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is now landed, but that scaffold stays intentionally sample-only and outside the first shared-request trio while the shared loader packet keeps the blocked trace-events runtime-substrate handoff explicit.
- `Documentation/zigux/freeze-map.md` also keeps `kernel/trace/ring_buffer.c` in `Study / Boundary Only`, so tracepoint-registration lifecycle wiring, thread creation, and any future trace-events loader path remain blocked until that boundary is reopened with Architecture Council evidence.

## Gates

1. run the shipped shared build-only checker first
- `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test`
- `python3 scripts/zigux/check-phase9-build-only-surface.py`

2. replay the focused shared runtime-loader packet
- `make -C zigux phase9-runtime-loader-shared-tests`

3. replay the bundled Phase 9 runtime build so the same loader-stage vocabulary and lifecycle-parity evidence stay visible beside the broader samples and surveys
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- `make -C zigux phase9`

4. keep the removed dedicated validator surfaces absent on current `master`
- there is no dedicated `scripts/zigux/validate-phase9.py`
- there is no `make -C zigux phase9-validate` route
- shared release-discipline follow-through belongs in `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase9-build-only-surface.py`

These gates keep the substrate-plan note tied to the actual tests, docs, and samples that prove it, instead of leaving the shared loader-stage vocabulary as prose-only context or pointing back to removed validator routes.

## Non-goals

This slice should not yet claim:

- a working runtime module loader
- `module_init` or `module_exit` parity
- real `register_kretprobe()` execution
- tracepoint registration parity
- thread creation or scheduling parity
- a completed `runtime_trace_events_loader.zig` implementation

## Next bounded step

If this lane reopens, keep it narrow: either let another runtime starter adopt the same shared request surface, or add one explicitly owned command or environment activation field after the Phase 8 tooling posture provides a truthful control-plane source.
