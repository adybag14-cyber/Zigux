# Phase 7 String Helpers Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- scope: first low-risk runtime-safe string helper batch only
- product boundary:
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- can be validated with a focused Zig gate before deeper formatting, escaping, or allocation-backed helpers are attempted

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

The Phase 5 roadmap keeps approved reference idioms under four sample anchors in `samples/zigux/`, and no `samples/zigux/*string*` Phase 5 reference sample is expected here; treat any new `samples/zigux/*string*.zig` claim as a separate roadmap-boundary decision instead of silently folding it into this helper slice.

## Gates

1. run the focused Zig Phase 7 helper tests
- `zig build test --build-file zigux/tests/phase7_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase7`

3. keep the dedicated no-string-sample boundary guard reviewable
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`

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
- deterministic space, octal, hex, special, and combined unescape cases derived from `lib/tests/string_helpers_kunit.c`
- in-place unescape behavior and bounded destination termination
- deterministic escape-space, special, null, octal, and hex output cases
- dictionary-limited `only` filtering plus `ESCAPE_APPEND` behavior for one newline-focused printable escape proof
- printable, non-printable, non-ascii, and non-printable-or-non-ascii passthrough filters over a hex-escaped bounded subset
- truncation accounting that returns the full would-be escaped length without promising an appended terminator
- the Phase 5-versus-Phase 7 boundary check that keeps `samples/zigux/` free of approved string-helper reference samples while pointing reviewers back to this helper packet

## Non-goals

This slice does not yet claim:

- parity for `skip_spaces()` and `strim()`
- parity for `string_get_size()`
- integer parsing helpers
- allocation-backed duplication helpers
- task-owned, file-owned, or device-managed quotable helper surfaces
- a new `samples/zigux/` string-helper reference sample

## Next bounded step

Leave this lane parked unless fresh repo inspection finds one more concrete Phase 7 helper need or a renewed Phase 5-versus-Phase 7 boundary drift.

If the string-helper family reopens, prefer `skip_spaces()` or `strim()` before heavier `string_get_size()` or parsing work, because those two helpers remain the smallest live `lib/string_helpers.c` leaf helpers that still fit the current runtime-safe Phase 7 boundary without widening into allocator-heavy, task-owned, file-owned, or device-managed surfaces.
