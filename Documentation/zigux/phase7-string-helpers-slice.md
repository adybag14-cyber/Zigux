# Phase 7 String Helpers Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- scope: first low-risk runtime-safe string helper batch only
- product boundary:
  - `lib/string_helpers.zig`
  - `samples/zigux/README.md`
  - `scripts/zigux/validate-phase7.py`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- can be validated with a focused Zig gate before deeper formatting, escaping, or allocation-backed helpers are attempted
- keep stronger ownership and pointer discipline explicit through bounded C-string prefix helpers, destination-size accounting, null-sentinel table handling, Linux-style size rendering cues, one count-prefixed integer-array starter, one copied-user-buffer integer-array wrapper, and one duplicated-replacement helper
- keep integration with validation substrate explicit through `zigux/tests/phase7_build.zig`, the dedicated `zigux/tests/phase7_string_helpers_survey.zig` survey gate, the shared `zig build test --build-file zigux/tests/phase7_build.zig --summary all` replay, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `scripts/zigux/validate-phase7.py`, and `make -C zigux phase7`

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

The Phase 5 roadmap keeps approved reference idioms under four sample anchors in `samples/zigux/`, and no `samples/zigux/*string*` Phase 5 reference sample is expected here; treat any new `samples/zigux/*string*.zig` claim as a separate roadmap-boundary decision instead of silently folding it into this helper slice.

## Gates

1. run the focused Zig Phase 7 helper tests
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

2. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `make -C zigux phase7-validate`

3. keep the helper wired through the Zigux convenience target
- `make -C zigux phase7`

4. keep the dedicated survey gate reviewable
- `zigux/tests/phase7_string_helpers_survey.zig`

5. keep the dedicated no-string-sample boundary guard reviewable
- `samples/zigux/README.md`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`

## Current parity surface

The current starter slice covers:

- `skip_spaces()`
- `strim()`
- `sysfs_streq()`
- `match_string()`
- `__sysfs_match_string()`
- `strreplace()`
- `kstrdup_and_replace()`
- `memcpy_and_pad()`
- `string_is_terminated()`
- `string_upper()`
- `string_lower()`
- `string_get_size()`
- `parse_int_array()`
- `parse_int_array_user()` over the bounded copied-user-buffer wrapper path
- `string_unescape()`
- `string_escape_mem()` over the bounded runtime-safe escape subset
- `kasprintf_strarray()` over the bounded sequential prefix-index ownership path
- `kfree_strarray()` over the bounded repeated-teardown-safe release path

The current tests check:

- leading whitespace skipping that stops at the first NUL
- in-place leading and trailing trimming that preserves bytes beyond the first NUL
- newline-tolerant sysfs equality
- bounded null-sentinel string table matching
- Linux-style `n = -1` string table scans that stop at the first NULL entry
- in-place replacement behavior that stops at the first NUL
- first-NUL-bounded duplicated replacement that returns an owned escaped-for-callers copy without mutating bytes beyond the exported C-string prefix
- truncation, exact-fit, and padding behavior for fixed-size destinations
- bounded termination checks that only scan the requested byte window
- bounded ASCII case conversion that stops at the first NUL
- Linux-style three-significant-figure size rendering for decimal and binary units, including no-space and no-bytes modifiers plus zero-block and truncated-buffer behavior
- mixed-base, negative-number, first-NUL-bounded, and empty-input integer-array parsing through the count-prefixed `parse_int_array()` starter
- copied-user-buffer, first-NUL-bounded, truncated-count, and short-buffer-fault behavior through `parse_int_array_user()`
- deterministic space, octal, hex, special, and combined unescape cases derived from `lib/tests/string_helpers_kunit.c`
- in-place unescape behavior and bounded destination termination
- deterministic escape-space, special, null, octal, and hex output cases
- dictionary-limited `only` filtering plus `ESCAPE_APPEND` behavior for one newline-focused printable escape proof
- printable, non-printable, non-ascii, and non-printable-or-non-ascii passthrough filters over a hex-escaped bounded subset
- truncation accounting that returns the full would-be escaped length without promising an appended terminator
- one allocator-backed `kasprintf_strarray()` proof that returns sequential `prefix-index` owned strings together with a trailing null-pointer view for C-style callers
- one `kfree_strarray()` proof that keeps first-NUL prefix handling, zero-count sentinel reuse, repeated teardown, and setup-failure cleanup safe
- the dedicated survey gate that keeps the roadmap anchor, helper replay, shared build route, and no-string-sample boundary reviewable together
- the Phase 5-versus-Phase 7 boundary check that keeps `samples/zigux/` free of approved string-helper reference samples while pointing reviewers back to this helper packet

## Non-goals

This slice does not yet claim:

- the broader allocation-backed duplication and string-array family beyond `kstrdup_and_replace()` and the current bounded starters
- task-owned, file-owned, or device-managed quotable helper surfaces
- a new `samples/zigux/` string-helper reference sample

## Next bounded step

Leave this lane parked unless fresh repo inspection finds one more concrete Phase 7 helper need or a renewed Phase 5-versus-Phase 7 boundary drift.

If the string-helper family reopens, prefer one bounded `kstrdup_quotable()` helper step before task-owned, file-owned, or device-managed follow-on work, because the live helper packet now covers the whitespace leaf pair, the dedicated survey gate, the bounded escape subset, `string_get_size()` sizing-path reviewability, the base count-prefixed integer-array starter, the copied-user-buffer integer-array wrapper, one duplicated-replacement helper, and one ownership-safe string-array starter.
