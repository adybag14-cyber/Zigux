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
- stay outside deeper parameter matching or escape handling
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
- quoted argument/value token splitting with in-place NUL termination

## Non-goals

This slice does not yet claim:

- parameter-name normalization beyond the raw token split
- escaped-quote handling beyond the Linux helper's bounded quote toggling
- exhaustive overflow compatibility with every `simple_strtoull()` corner case

## Next bounded step

Verify `next_arg()` against a broader mixed-spacing and quote-edge fixture set, then decide whether the lane should stay in `lib/cmdline.c` with another small parser primitive or close the starter cmdline slice.
