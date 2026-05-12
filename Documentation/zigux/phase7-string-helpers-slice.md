# Phase 7 String Helpers Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/string_helpers.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L04`
- scope: first low-risk runtime-safe string helper batch only
- lane state: the dedicated survey, dedicated no-string-sample boundary replay, dedicated manifest packet, shared build-wiring checker, shared validator, make-wrapper alignment note, and make-wrapper slice are still present, but current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`; keep this lane parked as a same-packet truthfulness repair until the helper packet itself is restored
- product boundary:
  - `lib/string_helpers.zig`
  - `Documentation/zigux/README.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/check-phase7-build-wiring.py`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - `zigux/tests/phase7_string_helpers_manifest.json`
  - `zigux/tests/phase7_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/Makefile`
- current-master gap: `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` remain the intended review surfaces for this lane, but they are missing from the live tree and should not be described as landed helper evidence until they are restored

## Why This Slice Exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

`lib/string_helpers.c` is a good first Phase 7 slice because it already contains several low-risk leaf helpers that:

- are runtime-adjacent without entering allocator-heavy or device-heavy paths
- benefit from explicit pointer and termination handling
- are still the right bounded formatting, escaping, and allocator-backed helper family to keep reviewable once the missing helper file is restored, without widening into broader ownership families
- keep stronger ownership and pointer discipline explicit through bounded C-string prefix helpers, destination-size accounting, null-sentinel table handling, Linux-style size rendering cues, first-NUL-bounded ASCII case-copy behavior that leaves trailing destination bytes untouched, one count-prefixed integer-array starter, one copied-user-buffer integer-array wrapper, one duplicated-replacement helper, and one quotable-log duplication helper
- keep integration with validation substrate explicit through `zigux/tests/phase7_build.zig`, the dedicated `zigux/tests/phase7_string_helpers_survey.zig` survey gate, `zigux/tests/phase7_string_helpers_manifest.json`, the shared `zig build test --build-file zigux/tests/phase7_build.zig --summary all` replay, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `.github/workflows/zigux-bootstrap.yml`, and `make -C zigux phase7`

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
The Phase 5 roadmap keeps approved reference idioms under four sample anchors in `samples/zigux/`, and no `samples/zigux/*string*` Phase 5 reference sample is expected here; treat any new `samples/zigux/*string*.zig` claim as a separate roadmap-boundary decision instead of silently folding it into this helper slice.

Current `master` still carries the note, manifest, survey, and no-string-sample boundary packet, but both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` are missing from the live tree. Treat this slice as a parked review packet with a missing implementation, not as a landed helper.

## Gates

1. keep the focused Zig Phase 7 helper tests explicit as a parked cross-packet target
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

The shared replay command above still describes the intended bundle route, but it is not a current string_helpers-local green claim while `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` remain absent from live `master`.

2. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py`
- `make -C zigux phase7-validate`

3. keep the helper wired through the Zigux convenience target as a parked shared route
- `make -C zigux phase7`

This shared make-wrapper route stays blocker-bearing until the missing helper-plus-test pair is restored; keep it documented as a parked bundle target instead of as evidence that the full string_helpers helper packet currently passes on `master`.

4. keep the dedicated survey gate reviewable
- `zigux/tests/phase7_string_helpers_survey.zig`

5. keep the dedicated no-string-sample boundary guard reviewable
- `samples/zigux/README.md`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`
- `make -C zigux phase7-string-helpers-sample-boundary`

6. keep the dedicated manifest packet explicit
- `zigux/tests/phase7_string_helpers_manifest.json`

## Current Parity Surface

The most recently described bounded slice covers:

- `skipSpaces()`
- `strim()`
- `sysfsStreq()`
- `matchString()`
- `sysfsMatchString()`
- `strreplace()`
- `kstrdupAndReplace()`
- `kstrdupQuotable()` over the bounded quotable-log escape path
- `memcpyAndPad()`
- `stringIsTerminated()`
- `stringUpper()`
- `stringLower()`
- `stringGetSize()`
- `parseIntArray()`
- `parseIntArrayUser()` over the bounded copied-user-buffer wrapper path
- `stringUnescape()`
- `stringUnescapeInplace()` over the bounded in-place runtime-safe wrapper path
- `stringEscapeMem()` over the bounded runtime-safe escape subset
- `stringEscapeStr()` over the bounded first-NUL string-oriented escape wrapper path
- `kasprintfStrarray()` over the bounded sequential prefix-index ownership path
- `kfreeStrarray()` over the bounded repeated-teardown-safe release path

The parked review packet still describes tests for:

- leading whitespace skipping that stops at the first NUL
- in-place leading and trailing trimming that preserves bytes beyond the first NUL
- newline-tolerant sysfs equality
- bounded null-sentinel string table matching
- Linux-style `n = -1` string table scans that stop at the first NULL entry
- in-place replacement behavior that stops at the first NUL
- first-NUL-bounded duplicated replacement that returns an owned escaped-for-callers copy without mutating bytes beyond the exported C-string prefix
- one allocator-backed quotable duplication proof that hex-escapes control bytes, quotes, and backslashes for log-safe callers while preserving null-input, first-NUL bounds, and allocation-failure cleanup
- truncation, exact-fit, and padding behavior for fixed-size destinations
- bounded termination checks that only scan the requested byte window
- bounded ASCII case conversion that stops at the first NUL and leaves destination bytes beyond the copied prefix untouched
- Linux-style three-significant-figure size rendering for decimal and binary units, including no-space and no-bytes modifiers plus zero-block and truncated-buffer behavior
- mixed-base, negative-number, first-NUL-bounded, and empty-input integer-array parsing through the count-prefixed `parseIntArray()` starter
- copied-user-buffer, first-NUL-bounded, truncated-count, and short-buffer-fault behavior through `parseIntArrayUser()`
- deterministic space, octal, hex, special, and combined unescape cases derived from `lib/tests/string_helpers_kunit.c`
- in-place unescape behavior and bounded destination termination, including the direct `string_unescape_inplace()` wrapper route
- exact-fit, terminator-only, and zero-capacity destination handling for `string_unescape()` so the helper's bounded write discipline stays reviewable
- deterministic escape-space, special, null, octal, and hex output cases
- dictionary-limited `only` filtering plus `ESCAPE_APPEND` behavior for one newline-focused printable escape proof
- printable, non-printable, non-ascii, and non-printable-or-non-ascii passthrough filters over a hex-escaped bounded subset
- first-NUL-bounded string-oriented escaping through `string_escape_str()` alongside the bounded `string_escape_mem()` subset
- truncation accounting that returns the full would-be escaped length without promising an appended terminator
- zero-capacity escape-destination accounting that still reports the full would-be escaped length without promising an appended terminator
- one allocator-backed `kasprintf_strarray()` proof that returns sequential `prefix-index` owned strings together with a trailing null-pointer view for C-style callers
- one `kfree_strarray()` proof that keeps first-NUL prefix handling, zero-count sentinel reuse, repeated teardown, and setup-failure cleanup safe
- the dedicated survey gate, the dedicated manifest packet, the shared make-wrapper checker, the dedicated build-wiring checker, the roadmap anchor, helper replay, shared build route, the workflow-backed bootstrap replay, the shared make-wrapper selftest-alignment control surface, the Linux-style `make -C zigux phase7-string-helpers-sample-boundary` replay route, and the no-string-sample boundary stay reviewable together
- the Phase 5-versus-Phase 7 boundary check that keeps `samples/zigux/` free of approved string-helper reference samples while pointing reviewers back to this helper packet

The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`, so the slice note, survey gate, no-string-sample boundary replay, and shared validator-backed route still have a machine-readable Phase 7 record even though the helper file and dedicated replay are currently missing from `master`.

## Non-goals

This slice does not yet claim:

- a restored landed helper packet on current `master` while `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` are still absent
- the broader allocation-backed duplication and string-array family beyond `kstrdup_and_replace()`, `kstrdup_quotable()`, and the current bounded starters
- the remaining task-owned, file-owned, or device-managed follow-ons: `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, and `devm_kasprintf_strarray()`
- a new `samples/zigux/` string-helper reference sample

## Next Bounded Step

The next honest reopen step is to restore `lib/string_helpers.zig` together with `zigux/tests/phase7_string_helpers.zig`, then rerun `python3 scripts/zigux/validate-phase7.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, and `zig build test --build-file zigux/tests/phase7_build.zig --summary all` before the lane is described as landed again.
Until those files are back on current `master`, keep this lane limited to same-packet truthfulness repairs in `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_survey.zig`, and `zigux/tests/phase7_string_helpers_sample_boundary.zig`.
If the helper packet is restored after that, keep the follow-through inside the bounded whitespace, size-rendering, quoting, escape, string-array, and no-sample boundary packet before widening into `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, or `devm_kasprintf_strarray()`.
