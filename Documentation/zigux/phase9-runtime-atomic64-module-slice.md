# Phase 9 Runtime Atomic64 Module Slice

This document tracks the first bounded Phase 9 runtime atomic64 starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- scope: lifecycle starter, selftest summary, dedicated Phase 9 test wiring, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_atomic64.zig`
  - `zigux/tests/runtime_atomic64_module.zig`
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The live Phase 9 tree had already identified `lib/atomic64_test.c` as the runtime pilot anchor, but it still stopped at a survey-only state. This slice lands the smallest honest runtime-facing follow-on step: a sample-backed lifecycle scaffold that reuses the existing atomic helper wrappers without claiming loadable-module parity.

## Landed starter surface

- module descriptor metadata naming the `lib/atomic64_test.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a 64-bit counter path using `zigux/helpers/atomic.zig`
- a selftest summary that groups the C anchor into arithmetic, bitwise, returning, swap, and guard-operation families
- dedicated Phase 9 tests and a `make -C zigux phase9` entry

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux module
- runtime module init and exit macro parity
- boot-time or module-load execution
- a C-vs-Zig differential gate for specific atomic64 operations

## Gates

1. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and add a small differential gate under `zigux/tests/runtime_atomic64_diff.zig` that turns a few `lib/atomic64_test.c` expectations into serialized or table-driven checks before attempting any broader runtime substrate work.
