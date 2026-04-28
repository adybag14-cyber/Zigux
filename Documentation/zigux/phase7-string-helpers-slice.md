# Phase 7 String Helpers Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- scope: first low-risk runtime-safe string helper batch only
- lane state: helper slice plus shared deterministic escape fixtures, shared wrapper-entrypoint coverage, and one allocator-explicit `parse_int_array()` bridge landed; parked unless a new `string_helpers.c` parity issue appears
- product boundary:
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- can be validated with a focused Zig gate before deeper formatting, escaping, or allocation-backed helpers are attempted

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane. Current `master` keeps string-helper reviewability in the helper and test bundle under `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, and `zigux/tests/phase7_build.zig`, while the four Phase 5 `samples/zigux/` anchors remain `bytestream_fifo`, `kobject_example`, `kretprobe_example`, and `trace_events_sample`.

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
- `skip_spaces()`
- `strim()`
- `memcpy_and_pad()`
- `string_is_terminated()`
- `string_upper()`
- `string_lower()`
- `string_get_size()` over the bounded SI and binary formatting subset
- `parse_int_array()` through an allocator-explicit counted-array wrapper that reuses the existing `get_options()` Zig port
- `string_unescape()`
- `string_unescape_inplace()`
- `string_unescape_any()`
- `string_unescape_any_inplace()`
- `string_escape_mem()` over the bounded runtime-safe escape subset
- `string_escape_mem_any_np()`
- `string_escape_str()`
- `string_escape_str_any_np()`

The current tests check:

- newline-tolerant sysfs equality
- bounded null-sentinel string table matching
- Linux-style `n = -1` string table scans that stop at the first NULL entry
- in-place replacement behavior that stops at the first NUL
- leading-whitespace skipping and in-place leading/trailing trimming that stop at the first NUL and preserve bytes beyond the terminator
- truncation, exact-fit, and padding behavior for fixed-size destinations
- bounded termination checks that only scan the requested byte window
- bounded ASCII case conversion that stops at the first NUL
- deterministic SI and binary `string_get_size()` formatting with a block-size multiplier
- `STRING_UNITS_NO_SPACE` and `STRING_UNITS_NO_BYTES` formatting flags plus snprintf-style truncation accounting for `string_get_size()`
- allocator-explicit `parseIntArray()` output that preserves the Linux counted-array shape from `get_options()` while returning `error.NoEntry` when no integers can be parsed
- deterministic space, octal, hex, special, and combined unescape cases derived from `lib/tests/string_helpers_kunit.c`
- shared deterministic escape fixtures under `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig` so the dedicated Phase 7 gate replays the landed escape-space, special, null, octal, hex, dictionary-limited, and passthrough-filter cases from one reviewable source
- in-place unescape behavior and bounded destination termination
- shared wrapper proofs that `string_unescape_inplace()`, `string_unescape_any()`, and `string_unescape_any_inplace()` preserve `UNESCAPE_ANY`, stop at the first written NUL, and leave trailing storage untouched
- deterministic escape-space, special, null, octal, and hex output cases through the shared fixture table
- dictionary-limited `only` filtering plus `ESCAPE_APPEND` behavior for one newline-focused printable escape proof through the shared fixture table
- printable, non-printable, non-ascii, and non-printable-or-non-ascii passthrough filters over a hex-escaped bounded subset through the shared fixture table
- truncation accounting that returns the full would-be escaped length without promising an appended terminator through one dedicated gate assertion
- shared wrapper proofs that `string_escape_mem_any_np()`, `string_escape_str()`, and `string_escape_str_any_np()` reuse the bounded `ESCAPE_ANY_NP` policy and stop at the first C-string terminator instead of walking tail bytes

## Non-goals

This slice does not yet claim:

- user-buffer handling parity for `parse_int_array_user()`
- integer parsing beyond the current counted-array bridge over the existing `get_options()` helper
- allocation-backed duplication helpers

## Next bounded step

Leave this lane parked unless fresh repo inspection finds one more concrete need to reopen inside the existing helper-and-gate surface. The remaining `string_helpers.c` work now trends toward user-buffer handling or broader allocation-backed helpers, which is a poorer fit for this parked Phase 7 leaf-helper lane.
