# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

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

This current slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
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
- `next_arg()`

The current tests check:

- signed integer parsing and comma handling
- Linux-style hyphen range expansion and validation-only counting
- descending-range early stop behavior
- memory-size suffix scaling with accurate parse-stop reporting
- exact bare-option matching for comma-delimited flags
- quoted argument/value splitting with in-place NUL termination and trimmed rest handling
- quoted bare-token parsing without inventing a value pointer

## Non-goals

This slice still does not yet claim:

- exhaustive overflow compatibility with every `simple_strtoull()` corner case
- broader parameter-name normalization or cross-subsystem callers beyond the local helper surface
- serialized C fixture generation for `next_arg()` edge cases

## Next bounded step

Add a small serialized fixture layer for `next_arg()` edge cases, or close this cmdline helper lane if no further Phase 7 review drift remains.
