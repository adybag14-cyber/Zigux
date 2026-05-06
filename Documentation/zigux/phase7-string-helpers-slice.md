# Phase 7 String Helpers Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- scope: first low-risk runtime-safe string helper batch only
- lane state: helper slice plus shared deterministic escape fixtures, bounded sample replay, and manifest-backed survey evidence landed; parked unless a new `string_helpers.c` parity issue appears
- product boundary:
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`
  - `samples/zigux/string_helpers_sample.zig`
  - `zigux/tests/phase7_string_helpers_sample_manifest.json`
  - `zigux/tests/phase7_string_helpers_sample_survey.zig`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- can be validated with a focused Zig gate before deeper formatting, escaping, or allocation-backed helpers are attempted

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
- `string_is_terminated()`
- `string_upper()`
- `string_lower()`
- `string_get_size()` over the bounded SI and binary formatting subset
- `string_unescape()`
- `string_escape_mem()` over the bounded runtime-safe escape subset

The current tests check:

- newline-tolerant sysfs equality
- bounded null-sentinel string table matching
- Linux-style `n = -1` string table scans that stop at the first NULL entry
- in-place replacement behavior that stops at the first NUL
- truncation, exact-fit, and padding behavior for fixed-size destinations
- bounded termination checks that only scan the requested byte window
- bounded ASCII case conversion that stops at the first NUL
- deterministic SI and binary `string_get_size()` formatting with a block-size multiplier
- `STRING_UNITS_NO_SPACE` and `STRING_UNITS_NO_BYTES` formatting flags plus snprintf-style truncation accounting for `string_get_size()`
- deterministic space, octal, hex, special, and combined unescape cases derived from `lib/tests/string_helpers_kunit.c`
- shared deterministic escape fixtures under `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig` so the dedicated Phase 7 gate replays the landed escape-space, special, null, octal, hex, dictionary-limited, and passthrough-filter cases from one reviewable source
- in-place unescape behavior and bounded destination termination
- deterministic escape-space, special, null, octal, and hex output cases through the shared fixture table
- dictionary-limited `only` filtering plus `ESCAPE_APPEND` behavior for one newline-focused printable escape proof through the shared fixture table
- printable, non-printable, non-ascii, and non-printable-or-non-ascii passthrough filters over a hex-escaped bounded subset through the shared fixture table
- truncation accounting that returns the full would-be escaped length without promising an appended terminator through one dedicated gate assertion
- the bounded `samples/zigux/string_helpers_sample.zig` replay for descriptor ownership, lifecycle transitions, newline-tolerant matching, binary size rendering, compact no-space-no-bytes formatting, and deterministic plus append-selected newline hex escaping through the shared Phase 7 build
- the manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate so the helper, shared fixtures, sample replay, and slice note stay aligned in one reviewable packet after the added compact-format and append-selected escape proofs

## Non-goals

This slice does not yet claim:

- parity for `parse_int_array()`
- integer parsing beyond the current formatter and escape surface
- allocation-backed duplication helpers

## Next bounded step

Leave this lane parked unless fresh repo inspection finds one more concrete need to reopen beyond the current bounded formatter-and-escape surface, such as a small `parse_int_array()` starter that is still clearly Phase 7-sized.
