# Phase 7 String Helpers Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/string_helpers.c`.

## Status

- `PHASE7_STATUS=starter_landed`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- `PHASE7_LANE_KEY=helper-local`
- lane-key note: `helper-local` keeps the expanded string-helpers starter packet separate from the Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes
- scope: keep the Phase 7 string-helpers lane limited to the expanded starter packet and the no-sample review boundary
- lane state: current `master` directly carries `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, and `samples/zigux/README.md`. Treat those helper-local files as the direct review packet for this slice. Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up and should not be counted here as direct helper-local proof unless a fresh reread materializes them again on current `master`.

## Why This Slice Exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

The current `string_helpers` state on `master` now carries an expanded starter packet that keeps the lowest-risk first-NUL, whitespace-sensitive, bounded size-formatting, bounded copy-and-pad, bounded duplicate-and-replace, bounded string-array ownership, bounded unescape, bounded string-escape, bounded quotable file-path duplication, bounded quotable-cmdline, bounded parse-int-array, and bounded case-conversion helpers reviewable while the broader device-managed follow-ons stay deliberately out of scope.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane. Current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample, so the dedicated boundary replay should keep that separation explicit while the expanded starter packet advances through helper-local review surfaces only.

## Gates

1. keep the expanded starter helper pair explicit
- `lib/string_helpers.zig`
- `zigux/tests/phase7_string_helpers.zig`

2. keep the helper-local survey packet explicit
- `zigux/tests/phase7_string_helpers_survey.zig`
- `zigux/tests/phase7_string_helpers_manifest.json`

3. keep the dedicated no-string-sample boundary guard reviewable
- `samples/zigux/README.md`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`

4. keep shared-control drift out of this helper-local slice unless it rematerializes on current `master`
- do not count `scripts/zigux/validate-phase7.py`
- do not count `scripts/zigux/check-phase7-make-wrapper.py`
- do not count `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- do not count `scripts/zigux/check-phase7-build-wiring.py`
- do not count `zigux/tests/phase7_build.zig`
- do not count `make -C zigux phase7-validate`
- do not count `make -C zigux phase7`
unless a fresh same-family reread proves those broader shared-control reminders are directly readable again on current `master`.

## Current Parity Surface

The expanded starter packet on current `master` covers:

- `skipSpaces()` and `skip_spaces()`
- `trimSpaces()` and `strim()`
- `sysfsStreq()` and `sysfs_streq()`
- `matchString()` and `match_string()`
- `sysfsMatchString()` and `__sysfs_match_string()`
- `stringGetSize()` and `string_get_size()`
- `stringUnescape()` and `string_unescape()`
- `stringUnescapeInplace()` and `string_unescape_inplace()`
- `stringUnescapeAny()` and `string_unescape_any()`
- `stringUnescapeAnyInplace()` and `string_unescape_any_inplace()`
- `stringEscapeMem()` and `string_escape_mem()`
- `stringEscapeMemAnyNp()` and `string_escape_mem_any_np()`
- `stringEscapeStr()` and `string_escape_str()`
- `stringEscapeStrAnyNp()` and `string_escape_str_any_np()`
- `kasprintfStrarray()` and `kasprintf_strarray()`
- `kfreeStrarray()` and `kfree_strarray()`
- `kstrdupAndReplace()` and `kstrdup_and_replace()`
- `kstrdupQuotable()` and `kstrdup_quotable()`
- `kstrdupQuotableFile()` and `kstrdup_quotable_file()`
- `kstrdupQuotableCmdline()` and `kstrdup_quotable_cmdline()`
- `parseIntArray()` and `parse_int_array()`
- `stringUpper()` and `string_upper()`
- `stringLower()` and `string_lower()`
- `memcpyAndPad()` and `memcpy_and_pad()`
- `strreplace()`

The current starter replay keeps these proofs explicit:

- leading whitespace skipping that stops at the first NUL
- in-place leading and trailing trimming that preserves bytes beyond the first exported C-string prefix
- newline-aware sysfs equality
- bounded null-sentinel table matching through the first NULL entry
- bounded size rendering with three significant figures, optional separator suppression, and truncation-safe output accounting
- bounded string unescaping across space, octal, hex, and special escape families, including in-place replays and unsupported-escape preservation
- bounded string escaping across space, special, null, octal, hex, append-limited dictionary mode, and string-wrapper mode, including truncation-safe output accounting
- bounded sequential string-array allocation with a NULL-terminated pointer view, C-string prefix handling, zero-length sentinel reuse, and caller-driven teardown
- allocator-backed duplicate-and-replace behavior that rewrites only the exported C-string prefix and leaves the source buffer untouched
- quoted-log-safe duplication that hex-escapes special logging hazards and double quotes while still stopping at the exported C-string prefix
- quoted file-path duplication that keeps an explicit `<unknown>` fallback for missing inputs while still escaping special characters through the same quotable path
- quoted cmdline duplication that collapses trailing NULs, replaces inter-argument NULs with spaces, and then reuses the quotable escape path inside caller-owned output
- bounded parse-int-array decoding for comma-separated lists, positive ranges, first-NUL and explicit-count limits, trailing-invalid-token stop behavior, and clean allocation-failure replay
- uppercase and lowercase copying that stops at the exported C-string boundary and truncates to caller-owned destination storage
- bounded memcpy-and-pad behavior that truncates long copies, pads short ones, and stays inside the provided source slice
- in-place replacement behavior that stops at the first NUL
- the dedicated survey gate, helper-local manifest packet, and no-sample boundary replay

The current starter replay also keeps these ownership-focused boundaries explicit:

- `skipSpaces()`, `trimSpaces()`, and `strim()` stop at the exported C-string boundary and keep caller-provided slices visible
- exact-fit, terminator-only, and zero-capacity unescape destinations keep caller-owned output bounds explicit
- `stringEscapeMem()` keeps append-limited and dictionary-mode output accounting inside caller-owned storage
- `stringEscapeMemAnyNp()`, `stringEscapeStr()`, and `stringEscapeStrAnyNp()` keep any-NP and first-NUL-bounded string-wrapper escaping inside caller-owned storage
- `kasprintfStrarray()` and `kfreeStrarray()` keep per-string allocations, reject overflow before sizing the NULL-terminated pointer view, preserve the shared zero-length sentinel, and keep teardown ownership explicit for caller-held results
- `kstrdupAndReplace()` returns caller-owned duplicated storage, applies replacements only inside the duplicated exported prefix, and leaves the source slice unchanged
- `kstrdupQuotable()` returns caller-owned duplicated storage, hex-escapes special logging hazards, and still stops at the exported C-string prefix
- `kstrdupQuotableFile()` keeps returned storage caller-owned, uses an explicit `<unknown>` fallback for missing file inputs, and otherwise reuses quotable escaping for already-materialized path strings
- `kstrdupQuotableCmdline()` keeps returned storage caller-owned, collapses trailing and inter-argument NUL separators inside duplicated command-line storage, and only then applies quotable escaping
- `parseIntArray()` and `parse_int_array()` keep the returned storage caller-owned, prefix the parsed count, and stop cleanly at the first invalid token, first NUL, or explicit count bound without widening beyond the successful decode set
- `stringUpper()`, `string_upper()`, `stringLower()`, and `string_lower()` keep case-conversion writes inside caller-provided destination storage and stop at the exported C-string boundary
- `memcpyAndPad()` and `strreplace()` keep writes inside caller-provided destination and exported prefix boundaries

## Non-goals

This expanded starter slice does not yet claim:

- the older parked missing-helper gap
- the broader shared-control packet that earlier runs described through validator, Makefile, workflow, or shared-build-route reminders
- the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet
- a new `samples/zigux/` string-helper reference sample

## Next Bounded Step

Keep the dedicated survey and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on, and reopen only when that helper-local non-goal lands or the no-sample boundary drifts on current `master`.
Route any shared validator, Makefile, workflow, tests-root, or docs-root drift to the separate Phase 7 shared-control lanes only after a fresh same-family reread proves those broader reminders are directly readable again on current `master`.
