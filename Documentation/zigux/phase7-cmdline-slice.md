# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

* `PHASE7_STATUS=parked`
* `PHASE7_SLICE=cmdline-runtime-leaf`
* `PHASE7_LANE_KEY=P7-L05`
* scope: first low-risk runtime-safe parsing helpers only
* lane state: the helper, dedicated test, dedicated survey, committed manifest packet, and committed `nextArg()` fixture remain visible on current `master`; keep the cmdline packet parked unless a fresh parity, survey, manifest, fixture, or same-slice reminder drift appears inside that landed helper-local packet
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
* shared-route note: the broader shared `zigux/tests/phase7_build.zig` route is still parked on current `master` because the sibling string-helpers pair `lib/string_helpers.zig` plus `zigux/tests/phase7_string_helpers.zig` remains absent, but that is a cross-packet Phase 7 issue rather than a cmdline-local blocker

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
- do not widen into shell, process, runtime-loader, or sample-owned execution behavior
- keep range parsing, suffix-aware size parsing, exact bare-option matching for comma-delimited flags, and `nextArg()` token splitting reviewable through deterministic Zig replays
- keep empty-input handling keeps `param` and `rest` borrowed from the caller slice
- keep leading-whitespace handling keeps the Linux-style empty sentinel token
- keep mixed-whitespace trimming and caller-owned buffer slicing explicit instead of widening into ownership-heavy follow-on helpers

Current repo reality is narrower only at the shared bundle level: on `2026-05-12`, direct current `master` reads returned this slice note together with `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, and `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`.
That means the cmdline-local helper packet is still landed, while the broader shared `phase7_build.zig` replay remains parked because the sibling string-helpers helper-plus-test pair is still missing from live `master`.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under this slice, `Documentation/zigux/README.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/cmdline.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting cmdline as a fifth Phase 5 sample.

## Gates

1. keep the dedicated cmdline helper replay explicit

* `lib/cmdline.zig`
* `zigux/tests/phase7_cmdline.zig`

2. keep the dedicated cmdline survey gate explicit

* `zigux/tests/phase7_cmdline_survey.zig`
* `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
* `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7-cmdline-survey`

3. keep the machine-readable review record explicit

* `zigux/tests/phase7_cmdline_manifest.json`

4. keep the shared validator-first packet explicit

* `python3 scripts/zigux/validate-phase7.py`
* `python3 scripts/zigux/check-phase7-make-wrapper.py`
* `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
* `python3 scripts/zigux/check-phase7-build-wiring.py`
* `make -C zigux phase7-validate`

5. keep the shared Phase 7 helper gate explicit as a parked cross-packet target

The commands below still describe the intended shared replay surface, but they are not a current cmdline-local green claim while the missing string-helpers pair above remains absent from live `master`.

* `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7-test`
* `make -C zigux phase7`

## Current Repo Reality

Current `master` still exposes the bounded cmdline helper packet:

* `Documentation/zigux/phase7-cmdline-slice.md`
* `lib/cmdline.zig`
* `zigux/tests/phase7_cmdline.zig`
* `zigux/tests/phase7_cmdline_survey.zig`
* `zigux/tests/phase7_cmdline_manifest.json`
* `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`

Current `master` still does not expose the full shared Phase 7 helper bundle:

* `lib/string_helpers.zig` currently fails direct current-path reads
* `zigux/tests/phase7_string_helpers.zig` currently fails direct current-path reads

That means the dedicated cmdline helper replay and dedicated cmdline survey remain reviewable inside this slice, while the broader shared `phase7_build.zig` route is still a parked cross-packet target rather than a cmdline-local green claim.
Shared helper-lane ownership now lives in `Documentation/zigux/phase7-helper-lane-sequencing.md`; keep cmdline-local follow-through under `P7-L05` instead of reusing the shared sequencing lane.

The landed review text and tests still document these intended packet edges:

* `getOption()` and `getOptions()` preserve Linux-style range parsing, including validator-only counting paths
* `getOption()` clears caller-provided output on malformed signed and unsigned input so the bounded helper packet keeps that failure contract explicit instead of leaving stale caller state behind
* `getOption()` and `getOptions()` keep the oversized wrap contract explicit across both 32-bit boundary inputs and full-width unsigned parses: `2147483648` wraps to `-2147483648`, `-2147483649` wraps to `2147483647`, `18446744073709551615` wraps to `-1`, `-18446744073709551615` wraps to `1`, and the paired `getOptions()` replays preserve the same wrapped values together with the validation-only count path
* `memparse()` preserves suffix scaling, leading plus handling, and stop-index reporting
* exact bare-option matching for comma-delimited flags stays reviewable through `parseOptionStr()`
* caller-owned `nextArg()` buffer slicing stays explicit for `param`, `value`, and `rest`
* empty-input handling keeps `param` and `rest` borrowed from the caller slice
* leading-whitespace handling keeps the Linux-style empty sentinel token
* the dedicated helper replay, the dedicated survey gate, the dedicated `phase7-cmdline-survey` compile-check route, the committed manifest packet, the committed serialized fixture packet, the shared validator-first packet, the parked make-wrapper alignment note, and the no-sample boundary note are all still supposed to describe one bounded cmdline lane rather than separate ad hoc reminders

The intended helper entrypoints remain explicit:

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

Keep this cmdline slice parked unless fresh repo inspection finds one concrete cmdline parity, survey, manifest, fixture, or same-slice reminder drift inside the current helper packet.
If the family reopens, prefer one tiny same-packet follow-through around `getOption()`, `memparse()`, `parseOptionStr()`, `nextArg()`, or the committed `nextArg()` fixture before widening parsing policy.
Treat restoration of the broader shared `phase7_build.zig` route as a cross-packet follow-through tied to the missing string-helpers helper-plus-test pair rather than a cmdline-local blocker.

## Footer
