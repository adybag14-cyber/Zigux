# Phase 7 Argv Split Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/argv_split.c`.

## Status

- `PHASE7_STATUS=active`
- `PHASE7_SLICE=argv-split-runtime-leaf`
- scope: first low-risk argv tokenization helpers only
- product boundary:
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/argv_split.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to the smallest runtime-safe ownership-preserving surface:

- whitespace-only argv tokenization
- first-NUL C-string bounds on both counting and splitting
- an explicit result object that owns the copied token buffer
- deterministic Zig-only validation without quote or shell expansion behavior

## Gates

1. run the focused Zig module tests
- `zig test lib/argv_split.zig`

2. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig`

## Current parity surface

The current starter slice covers:

- `count_argc()`
- `argv_split()`

The current tests check:

- repeated-whitespace collapsing into distinct argv entries
- blank-input handling
- first-NUL stop behavior for both `count_argc()` and `argv_split()`
- strict non-goal behavior where quote characters stay inside the returned tokens
- copied-buffer ownership so later source mutation does not affect split results

## Non-goals

This slice does not yet claim:

- shell-style quote parsing
- escape-sequence processing
- a null-terminated pointer-vector API that mirrors the raw kernel allocation layout exactly
- generated C fixture parity artifacts

## Next bounded step

Add a small serialized fixture layer that cross-checks the whitespace-only split behavior against `lib/argv_split.c`, or close this lane if the current starter helper surface is considered sufficient for Phase 7.
