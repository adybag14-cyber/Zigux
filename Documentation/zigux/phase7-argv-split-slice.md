# Phase 7 Argv Split Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/argv_split.c`.

## Status

* `PHASE7_STATUS=parked`
* `PHASE7_SLICE=argv-split-runtime-leaf`
* `PHASE7_LANE_KEY=P7-L09`
* scope: first low-risk argument-vector parsing and teardown helpers only
* lane state: helper, dedicated survey, committed manifest packet, dedicated packet checker, shared validator, shared build-wiring checker, and parked make-wrapper alignment note landed; keep this helper slice parked unless a fresh parity gap appears inside the existing helper, survey, manifest, checker, shared validator, or build-wiring packet
* current verification: a bounded 2026-05-12 replay confirmed `lib/argv_split.zig` and `zigux/tests/phase7_argv_split.zig` still compile together, but the broader shared `zigux/tests/phase7_build.zig` route is not currently replayable on live `master` because that build file still imports the missing sibling string-helpers pair `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`
* product boundary:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  * `Documentation/zigux/review-checklist.md`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase7.py`
  * `scripts/zigux/check-phase7-make-wrapper.py`
  * `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `scripts/zigux/check-phase7-argv-split-packet.py`
  * `scripts/zigux/check-phase7-build-wiring.py`
  * `lib/argv_split.zig`
  * `zigux/tests/README.md`
  * `zigux/tests/phase7_argv_split.zig`
  * `zigux/tests/phase7_argv_split_survey.zig`
  * `zigux/tests/phase7_argv_split_manifest.json`
  * `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  * `zigux/tests/phase7_build.zig`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

Phase 7 explicitly calls out `lib/argv_split.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe argument-vector helpers that:

* do not widen into shell, process, or runtime-loader behavior
* stay reviewable through deterministic Zig tests and one dedicated packet checker
* keep the exported C-style pointer view via `cArgv()` explicit for callers that need a null-terminated argv vector without turning the slice into a Phase 5 sample lane
* keep first-NUL C-string bounds on both counting and splitting
* keep stronger ownership and pointer discipline through the explicit `argvSplitWithArgc()` count mirror, `cArgv()` export, and `argvFree()` / `deinit()` teardown path
* keep copied-buffer ownership so later source mutation does not affect split results
* keep strict non-goal behavior where quote characters stay inside the returned tokens

Current repo reality is narrower only at the shared bundle level: on `2026-05-12`, direct current `master` reads returned this slice note together with `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, and `zigux/tests/fixtures/phase7_argv_split_vectors.zig`.
That means the argv_split-local helper packet is still landed, while the broader shared `phase7_build.zig` replay remains parked because the sibling string-helpers helper-plus-test pair is still missing from live `master`.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under this slice, `Documentation/zigux/README.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/argv_split.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting it as a fifth Phase 5 sample.

## Gates

1. keep the dedicated argv-split survey gate reviewable

* `zigux/tests/phase7_argv_split_survey.zig`

2. keep the committed packet checker explicit

* `python3 scripts/zigux/check-phase7-argv-split-packet.py`

3. keep the machine-readable review record explicit

* `zigux/tests/phase7_argv_split_manifest.json`

4. keep the focused parity fixtures explicit

* `zigux/tests/fixtures/phase7_argv_split_vectors.zig`

5. keep the shared validator-first packet explicit

* `python3 scripts/zigux/validate-phase7.py`
* `python3 scripts/zigux/check-phase7-make-wrapper.py`
* `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
* `python3 scripts/zigux/check-phase7-build-wiring.py`
* `make -C zigux phase7-validate`

6. keep the shared Phase 7 helper gate explicit as a parked cross-packet target

The commands below still describe the intended shared replay surface, but they are not a current argv_split-local green claim while the missing sibling imports above remain absent from live `master`.

* `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7`

## Current Repo Reality

Current `master` still exposes the bounded argv_split helper packet:

* `Documentation/zigux/phase7-argv-split-slice.md`
* `lib/argv_split.zig`
* `zigux/tests/phase7_argv_split.zig`
* `zigux/tests/phase7_argv_split_survey.zig`
* `zigux/tests/phase7_argv_split_manifest.json`
* `zigux/tests/fixtures/phase7_argv_split_vectors.zig`

Current `master` still does not expose the full shared Phase 7 helper bundle:

* `lib/string_helpers.zig` currently fails direct current-path reads
* `zigux/tests/phase7_string_helpers.zig` currently fails direct current-path reads

That means the dedicated argv_split helper replay and dedicated argv_split survey remain reviewable inside this slice, while the broader shared `phase7_build.zig` route is still a parked cross-packet target rather than an argv_split-local green claim.
Shared helper-lane ownership now lives in `Documentation/zigux/phase7-helper-lane-sequencing.md`; keep argv_split-local follow-through under `P7-L09` instead of reusing the shared sequencing lane.

## Current parity surface

The current landed slice covers the bounded `argv_split` review packet under `lib/argv_split.zig`, the dedicated `zigux/tests/phase7_argv_split.zig` helper replay, the dedicated `zigux/tests/phase7_argv_split_survey.zig` survey gate, the committed `zigux/tests/phase7_argv_split_manifest.json` manifest record, and the focused `zigux/tests/fixtures/phase7_argv_split_vectors.zig` fixture module.

The current tests keep these packet edges explicit:

* null-terminated pointer-vector access through `cArgv()`
* focused parity fixtures through `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
* copied whitespace separator runs are zeroed across the owned storage copy so each exported token stays in-place NUL-terminated
* separate non-blank callers keep owned storage, argv slices, and exported C-argv views distinct across results
* `argvFree()` and `deinit()` on one live non-blank result do not disturb another caller-owned split result
* non-blank cross-result teardown safety where `deinit()` or `argvFree()` on one live split keeps a sibling caller's storage, argv slices, and exported `cArgv()` view intact
* blank-input reuse of the empty exported argv view
* blank-input reuse of the empty storage sentinel without allocator space
* blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`, including shared empty-sentinel teardown beside another blank caller
* explicit `ArgvSplitResult.deinit()` clearing of exported storage, argv, and null-terminated sentinel views
* exported storage and argv views resetting back to the canonical empty sentinels after teardown
* allocator-failure cleanup so interrupted setup frees partially built ownership state before the helper returns
* safe and repeatable sentinel teardown through `argvFree()`
* explicit `argvFree()` ownership mirroring that keeps the `argv_free` teardown contract reviewable for C-style callers
* the dedicated packet checker, the shared validator-first packet, the make-wrapper alignment note, and the no-sample boundary note remain reviewable together, while the broader shared build replay stays parked until its missing sibling imports are restored

The helper entrypoints remain explicit:

- `argvSplitWithArgc()`
- `cArgv()`
- `argvFree()` plus `deinit()`

## Non-goals

This slice still does not yet claim:

* broader shell-quoting or command-line policy beyond the bounded helper packet
* a new `samples/zigux/` argv reference sample
* expansion into process startup, runtime-loader handoff, or later driver-facing ownership paths

## Next bounded step

Keep this slice parked unless fresh repo inspection finds one concrete `argv_split` parity, survey, manifest, fixture, or shared reminder drift inside the current helper packet.
If the family reopens, prefer one tiny same-packet follow-through around the already-landed `cArgv()`, exported-view clearing, blank-input sentinel, or teardown-safety packet before widening into broader parsing policy or sample-boundary work.

## Footer
