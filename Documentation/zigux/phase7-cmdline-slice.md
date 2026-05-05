# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=cmdline-runtime-leaf`
- scope: first low-risk parsing helpers only
- lane state: helper, fixture, and dedicated survey slice landed; parked unless a new `cmdline.c` parity issue appears
- product boundary:
  - `lib/cmdline.zig`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_cmdline_survey.zig`
  - `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
- can be validated with deterministic Zig-only tests

## Gates

1. run the focused Zig module tests
- `zig test lib/cmdline.zig`

2. run the dedicated cmdline helper replay
- `zig test zigux/tests/phase7_cmdline.zig`

3. run the dedicated cmdline survey gate
- `zig test zigux/tests/phase7_cmdline_survey.zig`

4. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig`

## Current parity surface

The current landed slice covers:

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
- C-style stop-at-NUL handling for bare-option scans
- serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, and empty-rest termination
- the dedicated survey gate keeps the roadmap anchor, focused helper replay, and shared `phase7_build.zig` compile-check path aligned around the same parked cmdline packet

## Non-goals

This slice still does not yet claim:

- exhaustive overflow compatibility with every `simple_strtoull()` corner case
- broader parameter-name normalization or cross-subsystem callers beyond the local helper surface

## Next bounded step

Move the next Phase 7 schedule to another unfinished leaf helper family. Reopen this lane only if fresh repo inspection finds one more real `cmdline.c` parity gap inside the existing helper, fixture, dedicated survey, or shared-gate surface.
