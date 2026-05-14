# Phase 7 String Helpers Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/string_helpers.c`.

## Status

- `PHASE7_STATUS=starter_landed`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L04`
- lane-key note: `P7-L04` remains the packet-local helper marker for the expanded string-helpers starter packet; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with the separate Phase 7 shared-control lanes
- scope: keep the Phase 7 string-helpers lane limited to the expanded starter packet and the no-sample review boundary
- lane state: current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`, while the dedicated survey, dedicated no-string-sample boundary replay, dedicated manifest packet, shared build-wiring checker, shared validator, make-wrapper alignment note, shared build route, and Linux-style `make -C zigux phase7` replay keep that expanded starter packet reviewable without claiming the broader parked family is fully landed

## Why This Slice Exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

The current `string_helpers` state on `master` now carries an expanded starter packet that keeps the lowest-risk first-NUL, whitespace-sensitive, bounded size-formatting, bounded copy-and-pad, bounded unescape, and bounded string-escape helpers reviewable while the broader family stays deliberately out of scope.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane. Current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample, so the dedicated boundary replay should keep that separation explicit while the expanded starter packet advances through helper-local review surfaces only.

## Gates

1. keep the expanded starter tests explicit
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
- `zigux/tests/phase7_string_helpers.zig`

2. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py`
- `make -C zigux phase7-validate`

3. keep the helper wired through the shared Phase 7 convenience route
- `make -C zigux phase7`

4. keep the dedicated survey gate reviewable
- `zigux/tests/phase7_string_helpers_survey.zig`

5. keep the dedicated no-string-sample boundary guard reviewable
- `samples/zigux/README.md`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`
- `make -C zigux phase7-string-helpers-sample-boundary`

6. keep the dedicated manifest packet explicit
- `zigux/tests/phase7_string_helpers_manifest.json`

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
- bounded memcpy-and-pad behavior that truncates long copies, pads short ones, and stays inside the provided source slice
- in-place replacement behavior that stops at the first NUL
- the dedicated survey gate, manifest packet, no-sample boundary replay, shared validator route, shared build route, and Linux-style `make -C zigux phase7` replay

## Non-goals

This expanded starter slice does not yet claim:

- the older parked missing-helper gap
- the broader full-family packet that still leaves `parse_int_array()`, `kstrdup_quotable()`, `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, `kstrdup_and_replace()`, `kasprintf_strarray()`, `kfree_strarray()`, or `devm_kasprintf_strarray()` outside the current `master` helper packet
- a new `samples/zigux/` string-helper reference sample

## Next Bounded Step

The next bounded follow-through should stay inside the expanded starter packet.
The next bounded follow-through should keep the expanded starter packet truthful across the survey, manifest, boundary replay, validator, and slice note, then take one deeper helper-local expansion step only after that packet stays aligned again.
