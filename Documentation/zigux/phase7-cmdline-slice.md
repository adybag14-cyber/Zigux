# Phase 7 Cmdline Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

- `PHASE7_STATUS=active`
- `PHASE7_SLICE=cmdline-runtime-leaf`
- scope: first low-risk parsing helpers only
- product boundary:
  - `lib/cmdline.zig`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This starter slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
- stay outside deeper argument tokenization and in-place quote rewriting
- can be validated with deterministic Zig-only tests

## Gates

1. run the focused Zig module tests
- `zig test lib/cmdline.zig`

2. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig`

## Current parity surface

The current starter slice covers:

- `get_option()`
- `get_options()`
- `memparse()`
- `parse_option_str()`

The current tests check:

- signed integer parsing and comma handling
- Linux-style hyphen range expansion and validation-only counting
- descending-range early stop behavior
- memory-size suffix scaling with accurate parse-stop reporting
- exact bare-option matching for comma-delimited flags

## Non-goals

This slice does not yet claim:

- parity for `next_arg()`
- quoted argument splitting
- in-place parameter/value token rewriting
- exhaustive overflow compatibility with every `simple_strtoull()` corner case

## Next bounded step

Port `next_arg()` with focused quoted-value fixtures and keep it inside the same Phase 7 leaf-helper lane rather than widening into unrelated parser families.
