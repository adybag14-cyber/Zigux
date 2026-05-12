# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

* `PHASE7_STATUS=parked`
* `PHASE7_SLICE=cmdline-runtime-leaf`
* `PHASE7_LANE_KEY=P7-Y06`
* scope: first low-risk runtime-safe parsing helpers only
* lane state: helper, dedicated survey, committed manifest packet, shared build-wiring checker, shared validator, and parked make-wrapper alignment note landed; keep this helper slice parked unless a fresh parity gap appears inside the existing helper, survey, manifest, fixture, or shared review packet
* product boundary:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  * `Documentation/zigux/review-checklist.md`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase7.py`
  * `scripts/zigux/check-phase7-make-wrapper.py`
  * `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `scripts/zigux/check-phase7-build-wiring.py`
  * `lib/cmdline.zig`
  * `zigux/tests/README.md`
  * `zigux/tests/phase7_cmdline.zig`
  * `zigux/tests/phase7_cmdline_survey.zig`
  * `zigux/tests/phase7_cmdline_manifest.json`
  * `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
  * `zigux/tests/phase7_build.zig`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
- do not widen into shell, process, runtime-loader, or sample-owned execution behavior
- keep range parsing, suffix-aware size parsing, exact bare-option matching for comma-delimited flags, and `nextArg()` token splitting reviewable through deterministic Zig replays
- keep empty-input handling keeps `param` and `rest` borrowed from the caller slice
- keep leading-whitespace handling keeps the Linux-style empty sentinel token
- keep mixed-whitespace trimming and caller-owned buffer slicing explicit instead of widening into ownership-heavy follow-on helpers

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under this slice, `Documentation/zigux/README.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/cmdline.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting cmdline as a fifth Phase 5 sample.

## Gates

1. keep the dedicated cmdline survey gate reviewable

* `zigux/tests/phase7_cmdline_survey.zig`

2. keep the machine-readable review record explicit

* `zigux/tests/phase7_cmdline_manifest.json`

3. keep the committed serialized `next_arg()` fixture packet explicit

* `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`

4. keep the shared validator-first packet explicit

* `python3 scripts/zigux/validate-phase7.py`
* `python3 scripts/zigux/check-phase7-make-wrapper.py`
* `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
* `python3 scripts/zigux/check-phase7-build-wiring.py`
* `make -C zigux phase7-validate`

5. keep the shared Phase 7 helper gate explicit

* `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7-test`
* `make -C zigux phase7`

## Current parity surface

The current landed slice covers the bounded cmdline review packet under `lib/cmdline.zig`, the dedicated `zigux/tests/phase7_cmdline.zig` helper replay, the dedicated `zigux/tests/phase7_cmdline_survey.zig` survey gate, the committed `zigux/tests/phase7_cmdline_manifest.json` review record, and the committed serialized `next_arg()` edge fixtures under `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`.

The current tests keep these packet edges explicit:

* `getOption()` and `getOptions()` preserve Linux-style range parsing, including validator-only counting paths
* `getOption()` and `getOptions()` keep the oversized wrap contract explicit: `2147483648` wraps to `-2147483648`, `-2147483649` wraps to `2147483647`, and the paired `getOptions("2147483648,-2147483649", ...)` replay preserves the same wrapped values together with the validation-only count path
* `memparse()` preserves suffix scaling, leading plus handling, and stop-index reporting
* exact bare-option matching for comma-delimited flags stays reviewable through `parseOptionStr()`
* caller-owned `nextArg()` buffer slicing stays explicit for `param`, `value`, and `rest`
* empty-input handling keeps `param` and `rest` borrowed from the caller slice
* leading-whitespace handling keeps the Linux-style empty sentinel token
* serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination
* the dedicated survey gate, the committed manifest packet, the committed fixture packet, the shared validator-first packet, the parked make-wrapper alignment note, and the no-sample boundary note stay reviewable together instead of drifting into separate ad hoc reminders

The helper entrypoints remain explicit:

* `getOption()`
* `getOptions()`
* `memparse()`
* `parseOptionStr()`
* `nextArg()`

## Non-goals

This slice still does not yet claim:

* shell-style quoting policy beyond the bounded helper packet
* process startup, runtime-loader handoff, or broader boot-parameter ownership policy
* a new `samples/zigux/` cmdline reference sample

## Next bounded step

Keep this slice parked unless fresh repo inspection finds one concrete cmdline parity, survey, manifest, fixture, or shared reminder drift inside the current helper packet.
The earlier docs-root follow-through is now closed: current `master` already keeps the fuller Phase 5 no-cmdline-sample packet explicit from `Documentation/zigux/README.md`, including `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` beside the landed cmdline helper, survey, manifest, fixture, and shared build entrypoint.
If the family reopens after that docs-root sync, prefer one tiny same-packet follow-through around the already-landed oversized-wrap replay, the `nextArg()` caller-slice ownership packet, the serialized edge fixtures, or another shared review-surface wording repair before widening into broader parsing policy or another lane.

## Footer
