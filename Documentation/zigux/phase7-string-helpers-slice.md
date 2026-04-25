# Phase 7 String Helpers Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=active`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- scope: first low-risk runtime-safe string helper batch only
- product boundary:
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- can be validated with a focused Zig gate before deeper string escaping or allocation-backed helpers are attempted

## Gates

1. run the focused Zig Phase 7 helper tests
- `zig build test --build-file zigux/tests/phase7_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase7`

## Current parity surface

The current starter slice covers:

- `sysfs_streq()`
- `match_string()`
- `__sysfs_match_string()`
- `strreplace()`
- `memcpy_and_pad()`
- `string_upper()`
- `string_lower()`

The current tests check:

- newline-tolerant sysfs equality
- bounded null-sentinel string table matching
- Linux-style `n = -1` string table scans that stop at the first NULL entry
- in-place replacement behavior that stops at the first NUL
- truncation, exact-fit, and padding behavior for fixed-size destinations
- bounded ASCII case conversion that stops at the first NUL

## Non-goals

This slice does not yet claim:

- parity for `string_get_size()`
- integer parsing helpers
- escape or unescape helpers
- allocation-backed duplication helpers

## Next bounded step

Port either `string_unescape()` or `string_escape_mem()` with a deterministic fixture set derived from `lib/string_helpers.c`, then extend the Phase 7 gate with those byte-level transformations instead of growing more wrapper-only coverage around the current starter helpers.
