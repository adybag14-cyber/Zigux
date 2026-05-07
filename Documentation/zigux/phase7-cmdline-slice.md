# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=cmdline-runtime-leaf`
- scope: first low-risk parsing helpers only
- lane state: helper, fixture, dedicated survey, shared validator, and make-wrapper slice landed; parked unless a new `cmdline.c` parity issue appears
- product boundary:
  - `lib/cmdline.zig`
  - `samples/zigux/README.md`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_cmdline_survey.zig`
  - `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
- can be validated with deterministic Zig-only tests

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under this slice, `samples/zigux/README.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig` instead of counting it as a fifth Phase 5 sample.

## Gates

1. run the focused Zig module tests
- `zig test lib/cmdline.zig`

2. run the dedicated cmdline helper replay
- `zig test zigux/tests/phase7_cmdline.zig`

3. keep the serialized `next_arg()` edge-fixture layer explicit
- `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`

4. run the dedicated cmdline survey gate
- `zig test zigux/tests/phase7_cmdline_survey.zig`

5. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `make -C zigux phase7-validate`

6. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
- `make -C zigux phase7`

## Current parity surface

The current landed slice covers:

- `get_option()`
- `get_options()`
- `memparse()`
- `parse_option_str()`
- `next_arg()`

The current tests check:

- signed integer parsing and comma handling
- Linux-style hyphen range expansion, validation-only counting, and leading-plus numeric acceptance for `get_option()` and `get_options()`
- descending-range early stop behavior
- memory-size suffix scaling, leading-plus numeric acceptance, and accurate parse-stop reporting in `memparse()`
- exact bare-option matching for comma-delimited flags
- C-style stop-at-NUL handling for bare-option scans
- serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination
- the dedicated survey gate, the committed `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` fixture module, the exact `zig build test --build-file zigux/tests/phase7_build.zig --summary all` shared compile-check replay, and the shared `validate-phase7.py`, `check-phase7-make-wrapper.py`, `phase7_build.zig`, and `make -C zigux phase7-validate` plus `make -C zigux phase7` routes keep the roadmap anchor, the leading-plus numeric replay, serialized `next_arg()` replay, focused helper replay, and Linux-style validator-first packet aligned around the same parked cmdline slice

## Non-goals

This slice still does not yet claim:

- exhaustive overflow compatibility with every `simple_strtoull()` corner case
- broader parameter-name normalization or cross-subsystem callers beyond the local helper surface

## Next bounded step

Move the next Phase 7 schedule to another unfinished leaf helper family. Reopen this lane only if fresh repo inspection finds one more real `cmdline.c` parity gap inside the existing helper, fixture, dedicated survey, shared validator, exact shared compile-check replay, make-wrapper, or shared-gate surface.
