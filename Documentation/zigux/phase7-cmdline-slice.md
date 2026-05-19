# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

- `PHASE7_STATUS=helper_local_test_survey_manifest_anchor`
- `PHASE7_SLICE=cmdline-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L10`
- lane-key note: `P7-L10` keeps the dedicated cmdline packet separate from the broader Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons
- scope: keep the Phase 7 cmdline lane limited to the current helper-local slice anchor, dedicated replay, dedicated survey, and the no-standalone-cmdline-sample boundary
- lane state: current `master` directly carries `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `scripts/zigux/check-phase7-cmdline-packet.py`, and `samples/zigux/README.md`. Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned survey-backed packet.

## Why This Slice Exists

Phase 7 is where Zigux starts carrying reusable runtime helper families in product-facing locations.

The current `cmdline` state on `master` now carries a bounded helper-local packet around exact bare-option matching, Linux-style option and range decoding, quoted and key-value argument splitting, signed and unsigned memory parsing, and survey-backed packet reviewability while keeping broader shared-control follow-ons outside this same helper family.

This is intentionally not a Phase 5 `samples/zigux/` delivery lane. Current `master` still ships no standalone `samples/zigux/*cmdline*` reference sample, so the dedicated boundary reminder should keep that separation explicit while the Phase 7 cmdline helper stays reviewable through helper-local surfaces only.

## Gates

1. keep the helper-local implementation explicit
- `lib/cmdline.zig`

2. keep the current helper-local review packet explicit
- `Documentation/zigux/phase7-cmdline-slice.md`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_cmdline_survey.zig`
- `zigux/tests/phase7_cmdline_manifest.json`
- `scripts/zigux/check-phase7-cmdline-packet.py`

3. keep the no-standalone-cmdline-sample boundary explicit
- `samples/zigux/README.md`

4. keep adjacent Phase 7 families and shared-control surfaces out of this packet unless a fresh reread says otherwise
- do not count `Documentation/zigux/phase7-string-helpers-slice.md`
- do not count `Documentation/zigux/phase7-argv-split-slice.md`
- do not count `Documentation/zigux/phase7-rbtree-slice.md`
- do not count shared validator, Makefile, workflow, or build-route reminders here even when they are readable as non-owner evidence

## Current Parity Surface

The current helper-local packet on `master` covers:

- `parseOptionStr()` and `parse_option_str`
- `getOption()` and `get_option`
- `getOptions()` and `get_options`
- `nextArg()` and `next_arg`
- `memparse()`

The current helper-local replay keeps these proofs explicit:

- exact bare-option matching that rejects key-value forms and keeps empty-entry behavior explicit
- Linux-style option parsing across signed, unsigned, comma-separated, and range-expanded inputs, including malformed-input and wraparound behavior
- quoted and key-value argument splitting that preserves the remaining borrowed suffix without widening beyond the first exported C-string boundary
- decimal, hexadecimal, octal, signed, and suffix-aware memory parsing with explicit no-conversion and signed-clamping behavior
- dedicated helper-local replay, survey, manifest, and checker coverage rooted at `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, and `scripts/zigux/check-phase7-cmdline-packet.py`

The current helper-local replay also keeps these ownership and boundary rules explicit:

- `parseOptionStr()` stays bounded to exact comma-delimited bare options inside the exported C-string prefix
- `getOption()` and `getOptions()` keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior
- `nextArg()` and `next_arg()` keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary
- `memparse()` keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership
- the no-standalone-cmdline sample boundary stays helper-local only while `samples/zigux/README.md` keeps `*cmdline*` listed among the no-extra-sample reminders

## Non-goals

This helper-local Phase 7 cmdline slice does not yet claim:

- any standalone `samples/zigux/*cmdline*` sample-root delivery
- the separate `string_helpers`, `argv_split`, or `rbtree` helper families
- shared validator, Makefile, workflow, or tests-root reminder ownership
- widened shell-style quoting or escaping beyond the current helper-local packet

## Next Bounded Step

Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.
Route shared validator, Makefile, workflow, tests-root, sample-root, and broader docs-root follow-through to the separate Phase 7 shared-control lanes.
