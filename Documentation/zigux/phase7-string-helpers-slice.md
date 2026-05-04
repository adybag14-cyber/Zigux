# Phase 7 String Helpers Slice

This document starts a bounded Phase 7 runtime leaf-helper slice for Zigux.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- scope: first low-risk runtime-safe string helper batch only
- lane state: helper slice plus shared deterministic escape fixtures, shared wrapper-entrypoint coverage, small allocator-backed `parse_int_array()` and `parse_int_array_user()` starters, one log-safe `kstrdup_quotable()` duplication helper, one ownership-safe `kstrdup_and_replace()` duplication helper, and one sequential string-array allocator plus teardown starter landed; parked unless a new `string_helpers.c` parity issue appears
- product boundary:
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_manifest.json`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- can be validated with a focused Zig gate before deeper formatting, escaping, or allocation-backed helpers are attempted

This current slice keeps the work bounded to runtime-safe leaf helpers with explicit integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, and `zigux/tests/phase7_build.zig`.

The survey-backed review packet stays rooted at `repo_root` through `zigux/tests/phase7_build.zig`, and the dedicated manifest in `zigux/tests/phase7_string_helpers_manifest.json` keeps the roadmap anchor, bounded helper surface, and directly coupled validation packet machine-readable together instead of drifting into helper-local notes.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane. Current `master` keeps string-helper reviewability in the helper and test bundle under `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, and `zigux/tests/phase7_build.zig`, while the four Phase 5 `samples/zigux/` anchors remain `bytestream_fifo`, `kobject_example`, `kretprobe_example`, and `trace_events_sample`.

Review note:
- helper-local test runs cannot import that fixture from outside the helper module path; keep both packets aligned when those serialized cases change
- no `samples/zigux/*string*` Phase 5 reference sample is expected here; `samples/zigux/README.md` remains the shared sample-root catalog while this leaf-helper evidence stays under the separate Phase 7 helper bundle
- keep `zigux/tests/phase7_string_helpers_sample_boundary.zig` aligned with that sample-root wording so the shipped no-string-sample rule stays machine-checked beside the helper-local survey gate instead of living only in prose
- the shared build-inventory fixture plus the dedicated string-helpers manifest stay part of this parked review packet, so `zigux/tests/fixtures/phase7_build_inventory.json`, `zigux/tests/phase7_string_helpers_manifest.json`, and the published `make -C zigux phase7-validate` wrapper path stay explicit instead of living only in the broader shared Phase 7 notes

## Gates

1. prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs
- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase7-build-inventory.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `make -C zigux phase7-validate`

2. run the focused Zig Phase 7 helper tests
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

3. keep the helper wired through the Zigux convenience target
- `make -C zigux phase7`

4. keep the helper-only roadmap, sample-root, and shared inventory review surface machine-checked from `repo_root`
- `zig test zigux/tests/phase7_string_helpers_survey.zig`
- `zig test zigux/tests/phase7_string_helpers_sample_boundary.zig`

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
- `string_unescape()`
- `string_unescape_inplace()`
- `string_unescape_any()`
- `string_unescape_any_inplace()`
- `string_escape_mem()` over the bounded runtime-safe escape subset
- `string_escape_mem_any_np()`
- `string_escape_str()`
- `string_escape_str_any_np()`
- `parse_int_array()` over the bounded allocator-backed starter path
- `parse_int_array_user()` over the bounded copy-and-parse starter path
- `kstrdup_quotable()` over the bounded escape-then-duplicate path for log-safe printable strings
- `kstrdup_and_replace()` over the bounded duplicate-then-rewrite ownership-safe path
- `kasprintf_strarray_raw()` over the bounded direct C-style null-terminated pointer-array starter path
- `kfree_strarray_raw()` over the bounded counted partial-teardown path for partially initialized string arrays
- `kasprintf_strarray()` over the bounded sequential prefix-index ownership path
- `kfree_strarray()` over the bounded repeated-teardown-safe release path

The current tests check:

- newline-tolerant sysfs equality
- bounded null-sentinel string table matching
- Linux-style `n = -1` string table scans that stop at the first NULL entry
- in-place replacement behavior that stops at the first NUL
- leading-whitespace skipping and in-place leading/trailing trimming that stop at the first NUL and preserve bytes beyond the terminator
- truncation, exact-fit, and padding behavior for fixed-size destinations
- bounded termination checks that only scan the requested byte window
- bounded ASCII case conversion that stops at the first NUL
- deterministic SI and binary `string_get_size()` formatting with a block-size multiplier, Linux-style rounding, odd block-size scaling, and huge-value saturation into the documented unit suffixes
- `STRING_UNITS_NO_SPACE` and `STRING_UNITS_NO_BYTES` formatting flags plus snprintf-style truncation accounting for `string_get_size()`
- deterministic space, octal, hex, special, and combined unescape cases derived from `lib/tests/string_helpers_kunit.c`
- shared deterministic escape fixtures under `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig` so the dedicated Phase 7 gate replays the landed escape-space, special, null, octal, hex, dictionary-limited, and passthrough-filter cases from one reviewable source
- in-place unescape behavior and bounded destination termination
- shared wrapper proofs that `string_unescape_inplace()`, `string_unescape_any()`, and `string_unescape_any_inplace()` preserve `UNESCAPE_ANY`, stop at the first written NUL, and leave trailing storage untouched
- deterministic escape-space, special, null, octal, and hex output cases through the shared fixture table
- dictionary-limited `only` filtering plus `ESCAPE_APPEND` behavior for one newline-focused printable escape proof through the shared fixture table
- printable, non-printable, non-ascii, and non-printable-or-non-ascii passthrough filters over a hex-escaped bounded subset through the shared fixture table
- truncation accounting that returns the full would-be escaped length without promising an appended terminator through one dedicated gate assertion
- shared wrapper proofs that `string_escape_mem_any_np()`, `string_escape_str()`, and `string_escape_str_any_np()` reuse the bounded `ESCAPE_ANY_NP` policy, stop at the first C-string terminator instead of walking tail bytes, and keep Linux's zero-sized destination behavior as a no-write length-only request
- allocator-backed `parse_int_array()` coverage that preserves Linux's count-prefixed output layout, reuses the existing `get_options()` base and sign semantics, stops at the first C-string terminator, truncates wide values to `i32`, and returns a no-entry error when the input contains no parseable integers
- shared `parse_int_array_user()` coverage that keeps the bounded copy window explicit before parsing, inserts a first-NUL terminator at the requested count boundary, and returns a no-entry error when the requested window is empty
- one allocator-backed `kstrdup_quotable()` proof that escapes newline, tab, backslash, and double-quote bytes through the existing bounded `ESCAPE_HEX` surface, preserves a trailing sentinel NUL, and keeps Linux's null-input behavior explicit
- one allocator-backed `kstrdup_and_replace()` proof that duplicates the first-NUL prefix before reusing `strreplace()`, preserves a trailing sentinel NUL on the returned owned string, keeps null input explicit, and leaves the source bytes untouched
- one allocator-backed `kasprintf_strarray_raw()` proof that keeps the direct C-style null-terminated pointer-array form explicit beside the higher-level Zig wrapper
- one shared `kasprintf_strarray_raw()` ownership proof that separate zero-count allocations stay distinct across callers instead of aliasing one sentinel-owned array while still tearing down safely through counted free paths
- one counted `kfree_strarray_raw()` proof that frees a partially initialized pointer-array prefix without requiring later entries to exist
- one allocator-backed `kasprintf_strarray()` proof that returns sequential `prefix-index` owned strings together with a trailing null-pointer view for C-style callers
- one `kfree_strarray()` proof that keeps first-NUL prefix handling, zero-count sentinel reuse, and repeated teardown safe

## Non-goals

This slice does not yet claim:

- integer parsing beyond the current formatter, bounded count-backed array starters, and escape surface
- the broader allocation-backed duplication family beyond the current `kstrdup_quotable()`, `kstrdup_and_replace()`, and bounded string-array starter helpers

## Next bounded step

Leave this lane parked unless fresh repo inspection finds one more concrete need to reopen beyond the current bounded formatter, escape, counted integer-array starter surface, bounded duplication helpers, and bounded string-array ownership helpers.
