# Phase 9 Shared Runtime Loader Substrate Plan

This document captures the bounded Phase 9 follow-up after the landed atomic64, bitmap, and kretprobe shared-request loader scaffolds, while keeping the adjacent trace-events loader scaffold explicit as a separate blocked pre-execution boundary, and now records the first shared request surface that all three shared-request loaders can emit.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=shared-runtime-loader-substrate-plan`
- `PHASE9_LANE_KEY=P6-L01`
- `PHASE9_SURVEYED_COMMIT=355b71d89807a217a6b7c405c996cbd623c48ca0`
- scope: shared request shape, shared loader-stage vocabulary, allocator-handoff and command-name review surfaces, atomic64 plus bitmap plus kretprobe handoff alignment, the explicit adjacent trace-events scaffold boundary, and an explicit low-risk path that now lands as `zigux/kernel/runtime_loader.zig` without claiming live runtime execution
- product boundary:
  - `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
  - `scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`
  - `scripts/zigux/check-phase9-loader-non-owner-boundary.py`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `samples/zigux/runtime_trace_events_loader.zig`
  - `zigux/tests/runtime_loader_non_owner_boundary_survey.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The live repo already ships three bounded loader-handoff surfaces:

- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

All three files currently stop at the same honest blocker: they can prepare a reviewable handoff plan, request runtime loading, and release without substrate, but they still have nowhere shared to send that handoff inside Zigux.

The live repo also now carries `samples/zigux/runtime_trace_events_loader.zig` as the bounded scaffold for the fourth Phase 9 pilot, but that scaffold remains adjacent to this first shared-request packet rather than part of its union: the trace-events packet still blocks thread creation, tracepoint-registration lifecycle wiring, and any `kernel/trace/ring_buffer.c` status change behind the study-only freeze boundary.

That makes the next useful step a shared substrate surface rather than another lane-local wording pass or a premature runtime-module implementation.

The current substrate-plan packet is pinned to `master` commit `355b71d89807a217a6b7c405c996cbd623c48ca0`.
This keeps the shared loader-stage vocabulary and handoff-alignment note reviewable against the same inspected repo state as the adjacent loader-gap survey packet.

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

The first shared-request union therefore still covers atomic64, bitmap, and kretprobe only, while the trace-events scaffold remains a separate pre-execution note until that packet can truthfully reuse the same handoff without implying trace-core parity or scheduler-facing ownership.

## Current acceptance boundary

The first shared substrate implementation is now ready because:

- atomic64, bitmap, and kretprobe can all export a common request shape without losing their current lane-specific facts
- the shared Phase 9 build can run focused tests for that common request shape
- the code still makes it impossible to confuse a bounded handoff with a real loadable runtime module
- the adjacent trace-events scaffold remains free to adopt the same request shape later, but it is still intentionally outside this first shared-request union so the implementation does not have to pretend thread creation or tracepoint registration are already solved
- the shared request keeps `command_name` reviewable as a narrow handoff clue that can later mirror `ExtractArgv0Result.command_name` without claiming a finished argv or environment control plane
- allocator ownership now stays machine-checkable through the shared `allocator_handoff` record before any real runtime loader exists

That still leaves the broader control plane blocked. Any future non-null `command_name` must keep a truthful Phase 8 owner such as `tools/lib/subcmd/exec-cmd.zig` and `ExtractArgv0Result.command_name`, and this slice still does not claim `Config.exec_path_env`, `PERF_EXEC_PATH`, `PATH`, or other environment-derived activation handling as runtime-loader behavior.

## Adjacent freeze boundaries

The shared request surface also stays parked beneath the nearby freeze-map boundaries:

- `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this substrate note must not imply scheduler transport ownership, polling, event-loop behavior, or workqueue-parity progress.
- `samples/zigux/runtime_trace_events.zig` remains the fourth Phase 9 pilot, and `samples/zigux/runtime_trace_events_loader.zig` now records a bounded pre-execution loader scaffold, but `zigux/tests/runtime_trace_events_manifest.json` still keeps the `runtime-trace-events-substrate-handoff` blocker explicit because the shared runtime substrate does not yet own tracepoint-registration execution, thread creation, or polling or event-loop wiring.
- `Documentation/zigux/freeze-map.md` also keeps `kernel/trace/ring_buffer.c` in `Study / Boundary Only`, so tracepoint-registration lifecycle wiring, thread creation, and any future trace-events shared-request binding or live loader path remain blocked until that boundary is reopened with Architecture Council evidence.

## Gates

1. run the dedicated shared-substrate checker first
- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`
- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`

2. replay the focused surveyed-commit alignment check for the shared loader packet
- `make -C zigux phase9-loader-commit-alignment-survey`

3. replay the focused non-owner-boundary check for the shared loader packet so the trace-events scaffold and the Phase 2 plus Phase 3 non-owner references stay explicit
- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`
- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`
- `make -C zigux phase9-non-owner-boundary-survey`

4. replay the focused runtime-loader survey packet that keeps this note aligned with the manifest, shared request surface, and sample-side loaders
- `zig test zigux/tests/runtime_loader_gap_survey.zig`
- `make -C zigux phase9-loader-gap-survey`

5. replay the shared Phase 9 runtime bundle so the same loader-stage vocabulary and lifecycle-parity evidence stay visible beside the broader samples and surveys
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- `make -C zigux phase9-test`

6. run the validator-first wrapper path when reviewing the whole Phase 9 packet
- `make -C zigux phase9-validate`
- `make -C zigux phase9`

These gates keep the substrate-plan note tied to the actual tests and samples that prove it, instead of leaving the shared loader-stage vocabulary as prose-only context.

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