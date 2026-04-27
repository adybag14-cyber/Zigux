# Phase 9 Shared Runtime Loader Substrate Plan

This document captures the next bounded Phase 9 follow-up after the landed bitmap and kretprobe loader scaffolds.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=shared-runtime-loader-substrate-plan`
- scope: shared request shape, shared loader-stage vocabulary, bitmap and kretprobe handoff alignment, and an explicit low-risk path toward `zigux/kernel/runtime_loader.zig`
- product boundary:
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

## Recommended first shared substrate

The next code step should stay intentionally small:

1. add `zigux/kernel/runtime_loader.zig` as a pure data-and-state surface only
2. define one shared stage enum for the loader handoff lifecycle
3. define one shared request struct for the common module identity and lifecycle facts
4. carry lane-specific details in a narrow tagged payload rather than separate unrelated loader state machines
5. keep every path testable through `zigux/tests/phase9_build.zig` without introducing real kernel loader hooks

The initial shared request should keep these common fields explicit:

- module name
- Linux anchor path
- entry symbol
- exit symbol
- `requires_runtime_substrate`
- `provides_selftest_hook`
- sample handoff stage
- lane kind such as bitmap or kretprobe

The first lane payloads should stay small:

- bitmap payload: summary snapshot only
- kretprobe payload: register API, unregister API, symbol name, `maxactive`, private-data bytes, and current bookkeeping summary

## Suggested acceptance boundary

The first shared substrate implementation is ready once:

- bitmap and kretprobe can both export a common request shape without losing their current lane-specific facts
- the shared Phase 9 build can run focused tests for that common request shape
- the code still makes it impossible to confuse a bounded handoff with a real loadable runtime module
- the trace-events lane remains free to adopt the same request shape later without forcing the first implementation to solve thread creation or tracepoint registration

## Non-goals

This slice should not yet claim:

- a working runtime module loader
- `module_init` or `module_exit` parity
- real `register_kretprobe()` execution
- tracepoint registration parity
- thread creation or scheduling parity
- a completed `runtime_trace_events_loader.zig` implementation

## Next bounded step

Implement a pure shared `zigux/kernel/runtime_loader.zig` request surface, adapt the bitmap and kretprobe loader scaffolds to emit that shared shape, and wire focused tests into `zigux/tests/phase9_build.zig` before attempting any real loader behavior.
