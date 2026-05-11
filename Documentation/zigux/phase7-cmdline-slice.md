# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status
* `PHASE7_STATUS=parked`
* `PHASE7_SLICE=cmdline-runtime-leaf`
* `PHASE7_LANE_KEY=P7-L08`
* scope: first low-risk parsing helpers only
* lane state: helper, fixture, dedicated survey, dedicated manifest, shared validator, shared build-wiring checker, and parked make-wrapper slice landed; keep this helper slice parked unless a fresh parity gap appears inside the existing helper, fixture, dedicated survey, dedicated manifest, shared validator, shared build-wiring checker, or make-wrapper packet
* product boundary:
  * `Documentation/zigux/README.md`
  * `lib/cmdline.zig`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `zigux/tests/phase7_cmdline.zig`
  * `zigux/tests/phase7_cmdline_survey.zig`
  * `zigux/tests/phase7_cmdline_manifest.json`
  * `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
  * `scripts/zigux/validate-phase7.py`
  * `scripts/zigux/check-phase7-make-wrapper.py`
  * `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `scripts/zigux/check-phase7-build-wiring.py`
  * `zigux/tests/phase7_build.zig`
  * `.github/workflows/zigux-bootstrap.yml`
  * `zigux/Makefile`

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe parsing helpers that:

* do not allocate
* can be validated with deterministic Zig-only tests

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under this slice, `Documentation/zigux/README.md`, `lib/cmdline.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` instead of counting it as a fifth Phase 5 sample.

## Gates

1. run the focused Zig module tests

* `zig test lib/cmdline.zig`

2. run the dedicated cmdline helper replay

* `zig test zigux/tests/phase7_cmdline.zig`

3. keep the serialized `next_arg()` edge-fixture layer explicit

* `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`

4. keep the machine-readable survey record explicit

* `zigux/tests/phase7_cmdline_manifest.json`

5. run the dedicated cmdline survey gate

* `zig test zigux/tests/phase7_cmdline_survey.zig`
6. keep the shared validator-first packet explicit

* `python3 scripts/zigux/validate-phase7.py`
* `python3 scripts/zigux/check-phase7-make-wrapper.py`
* `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
* `python3 scripts/zigux/check-phase7-build-wiring.py`
* `make -C zigux phase7-validate`

7. run the shared Phase 7 helper gate

* `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7`

## Current parity surface

The current landed slice covers:

* `get_option()`
* `get_options()`
* `memparse()`
* `parse_option_str()`
* `next_arg()`

The current tests check:
* signed integer parsing and comma handling
* validator-only `get_option()` acceptance plus Linux-style hyphen range expansion, validation-only counting, and leading-plus numeric acceptance for `get_option()` and `get_options()`
* descending-range early stop behavior
* memory-size suffix scaling, leading-plus numeric acceptance, and accurate parse-stop reporting in `memparse()`
* exact bare-option matching for comma-delimited flags, including leading and doubled-comma empty-option acceptance plus trailing-comma rejection
* C-style stop-at-NUL handling for bare-option scans
* serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination
* caller-owned buffer discipline for `next_arg()`: `nextArg()` writes NUL sentinels into the supplied mutable buffer and returns borrowed `param`, `value`, and `rest` slices into that same storage
* empty-input handling keeps `param` and `rest` borrowed from the caller slice instead of inventing owned storage
* leading-whitespace handling keeps the Linux-style empty sentinel token while trimming the following `rest`
* live helper-local readback plus attached Zig toolchain replay already confirm the still-unmirrored oversized-wrap contract: `getOption()` wraps `2147483648` to `-2147483648` and `-2147483649` to `2147483647`, while `getOptions("2147483648,-2147483649", ...)` preserves the same wrapped values and validation-only count without trapping
* the dedicated survey gate, the committed `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` fixture module, the committed `zigux/tests/phase7_cmdline_manifest.json` survey record, the exact `zig build test --build-file zigux/tests/phase7_build.zig --summary all` shared compile-check replay, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, the workflow-backed bootstrap replay in `.github/workflows/zigux-bootstrap.yml`, and the shared `validate-phase7.py`, `check-phase7-make-wrapper.py`, `check-phase7-make-wrapper-selftest-alignment.py`, `check-phase7-build-wiring.py`, `phase7_build.zig`, and `make -C zigux phase7-validate` plus `make -C zigux phase7` routes keep the roadmap anchor, the leading-plus numeric replay, serialized `next_arg()` replay, focused helper replay, machine-readable manifest, and Linux-style validator-first packet aligned around the same parked cmdline slice
The dedicated survey now imports the committed manifest under `zigux/tests/phase7_cmdline_manifest.json`, so the parked cmdline packet keeps its roadmap anchor, review surfaces, and ownership-focused `nextArg()` proofs explicit in one machine-readable record beside the sibling Phase 7 helper packets.

## Non-goals

This slice still does not yet claim:

* exhaustive overflow compatibility with every `simple_strtoull()` corner case
* broader parameter-name normalization or cross-subsystem callers beyond the local helper surface

## Next bounded step

Keep the helper slice parked for behavior, fixtures, and shared reminder wording except for one still-open helper-local replay gap: live `lib/cmdline.zig` readback already shows oversized integer inputs stay runtime-safe by wrapping through the same truncated `int` results that `lib/cmdline.c` exposes from `get_option()` and `get_options()`, and the attached Zig toolchain replay from this lane confirmed the exact `2147483648`, `-2147483649`, and paired `2147483648,-2147483649` validation-count cases, but `zigux/tests/phase7_cmdline.zig` does not yet assert that contract directly.
The next honest same-lane follow-up is therefore specific rather than generic: add one dedicated oversized-wrap replay for those positive and negative `get_option()` inputs plus the paired `get_options()` wrapped-value and validation-count path, then refresh this slice note only if the published helper-local tests change what the parked packet can claim. If future drift is reminder-surface-only, treat any shared validator expansion as a separate bounded follow-up instead of implying that work has already landed.

## Footer
