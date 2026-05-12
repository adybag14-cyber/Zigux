# Phase 7 String Helpers Slice

This document tracks a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L03`
- scope: first low-risk runtime-safe string helper batch only
- lane state: helper slice plus shared deterministic escape fixtures, bounded sample replay, dedicated no-Phase-5-anchor boundary evidence, and manifest-backed survey evidence landed; parked unless a new `string_helpers.c` parity issue or a renewed Phase 5-versus-Phase 7 boundary drift appears
- product boundary:
  - `lib/string_helpers.zig`
  - `samples/zigux/README.md`
  - `samples/zigux/string_helpers_sample.zig`
  - `Documentation/zigux/phase7-string-helpers-slice.md`
  - `Documentation/zigux/README.md`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
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

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

The four approved Phase 5 anchors remain the bounded bytestream FIFO, kobject, kretprobe, and trace-events sample packets. The bounded sample replay added on this draft branch exists only to keep the landed helper contract reviewable through the shared Phase 7 lane, without recasting string helpers as a fifth Phase 5 sample family. The roadmap-backed Phase 7 product destination still remains `lib/string_helpers.zig`, with the draft `samples/zigux/string_helpers_sample.zig` packet kept as supporting review evidence rather than as a new approved sample-root idiom.

## Gates

1. run the focused Zig Phase 7 helper tests
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

2. keep the bounded sample packet reviewable through the same shared helper lane
- `samples/zigux/string_helpers_sample.zig`
- `zigux/tests/phase7_string_helpers_sample_manifest.json`
- `zigux/tests/phase7_string_helpers_sample_survey.zig`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`
- `samples/zigux/README.md`

3. keep the helper wired through the Zigux convenience target
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
- the bounded `samples/zigux/string_helpers_sample.zig` replay for descriptor ownership, lifecycle transitions, newline-tolerant matching, binary size rendering, compact no-space-no-bytes formatting, one exact-fit unescape destination proof, deterministic only-selected newline escaping, and append-selected newline hex escaping through the shared Phase 7 build
- the manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate so the helper, shared fixtures, sample replay, and slice note stay aligned in one reviewable packet after the added compact-format, exact-fit unescape boundary, only-selected newline escaping, and append-selected escape proofs
- the dedicated no-string-sample boundary packet in `samples/zigux/README.md` plus `zigux/tests/phase7_string_helpers_sample_boundary.zig` keeps the helper-backed replay explicit without recasting it as a fifth Phase 5 anchor
- the sample-facing note packet keeps the review route explicit for the draft branch while preserving the current `master` rule that string helpers still are not part of the frozen Phase 5 reference-sample set

## Non-goals

This slice does not yet claim:

- parity for `parse_int_array()`
- integer parsing beyond the current formatter and escape surface
- allocation-backed duplication helpers
- a new Phase 5 string-helper reference anchor

## Next bounded step

Leave this lane parked unless fresh repo inspection finds one more concrete need inside the current formatter-and-escape plus sample-boundary packet, such as a small helper-local parity fix or a renewed notes drift around the sample-backed review route.
