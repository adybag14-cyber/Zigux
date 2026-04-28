# Phase 9 Shared Runtime Loader Substrate Plan

This document captures the bounded Phase 9 follow-up after the landed bitmap and kretprobe loader scaffolds and now records the first shared request surface that both loaders can emit.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=shared-runtime-loader-substrate-plan`
- scope: shared request shape, shared loader-stage vocabulary, bitmap and kretprobe handoff alignment, the freeze-map boundary around scheduler-facing follow-up, and an explicit low-risk path that now lands as `zigux/kernel/runtime_loader.zig` without claiming live runtime execution
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/phase9_build.zig`

## Why this slice exists

The live repo already ships two bounded loader-handoff surfaces:

- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

Both files currently stop at the same honest blocker: they can prepare a reviewable handoff plan, request runtime loading, and release without substrate, but they still have nowhere shared to send that handoff inside Zigux.

That makes the next useful step a shared substrate surface rather than another lane-local wording pass or a premature runtime-module implementation.

## Shared facts already visible in the repo

The landed bitmap and kretprobe loaders already agree on several core ideas:

- a loader begins at `idle`, moves to `prepared`, then to `waiting_on_runtime_substrate`, and can fall back to `released_without_substrate`
- each lane exposes a bounded handoff plan rather than pretending the runtime substrate already exists
- each plan carries module identity, Linux anchor provenance, explicit init and exit symbol names, and the current sample lifecycle stage
- each lane keeps `requires_runtime_substrate` and `provides_selftest_hook` explicit instead of hiding them in prose

The main differences are lane-specific payload details:

- bitmap needs a bounded bitmap summary that can seed first-set, first-zero, weight, and bit-count review
- kretprobe needs explicit `register_kretprobe` and `unregister_kretprobe` naming plus symbol, `maxactive`, and private-data-size handoff facts

## Freeze-map and study boundary

This shared loader substrate is still adjacent to the roadmap's deeper runtime and scheduler-facing follow-up, so the current governance packet now keeps `Documentation/zigux/freeze-map.md` explicit beside the shared handoff note.

- `kernel/workqueue.c` remains `Study / Boundary Only`
- any status change for that scheduler-facing boundary still requires an Architecture Council decision
- the current Phase 9 loader substrate note does not carry a parity scorecard entry or an Architecture Council status-change request for `kernel/workqueue.c`
- accepted work in this slice stays limited to shared request-shape evidence, bounded handoff vocabulary, and explicit non-goals rather than worker-pool, queue-ownership, or live runtime execution claims

## Landed first shared substrate

The first shared code step stayed intentionally small:

1. add `zigux/kernel/runtime_loader.zig` as a pure data-and-state surface only
2. define one shared stage enum for the loader handoff lifecycle
3. define one shared request struct for the common module identity and lifecycle facts
4. carry lane-specific details in a narrow tagged payload rather than separate unrelated loader state machines
5. keep every path testable through `zigux/tests/phase9_build.zig` without introducing real kernel loader hooks

The landed shared request keeps these common fields explicit:

- module name
- Linux anchor path
- entry symbol
- exit symbol
- `requires_runtime_substrate`
- `provides_selftest_hook`
- sample handoff stage
- lane kind such as bitmap or kretprobe

The first lane payloads stay small:

- bitmap payload: summary snapshot only
- kretprobe payload: register API, unregister API, symbol name, `maxactive`, private-data bytes, and current bookkeeping summary

## Current acceptance boundary

The first shared substrate implementation is now ready because:

- bitmap and kretprobe can both export a common request shape without losing their current lane-specific facts
- the shared Phase 9 build can run focused tests for that common request shape
- the code still makes it impossible to confuse a bounded handoff with a real loadable runtime module
- the note keeps `kernel/workqueue.c` in `Study / Boundary Only` posture instead of silently widening the shared handoff into scheduler-facing ownership
- the trace-events lane remains free to adopt the same request shape later without forcing the first implementation to solve thread creation or tracepoint registration

## Non-goals

This slice should not yet claim:

- a working runtime module loader
- `module_init` or `module_exit` parity
- real `register_kretprobe()` execution
- a `kernel/workqueue.c` status change or scheduler-facing worker-pool ownership claim
- tracepoint registration parity
- thread creation or scheduling parity
- a completed `runtime_trace_events_loader.zig` implementation

## Next bounded step

If this lane reopens, keep it narrow: either let another runtime starter adopt the same shared request surface, or add one explicitly owned command or environment activation field after the Phase 8 tooling posture provides a truthful control-plane source while keeping `Documentation/zigux/freeze-map.md` and the `kernel/workqueue.c` study boundary explicit.
