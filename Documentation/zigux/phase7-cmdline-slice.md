# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

* `PHASE7_STATUS=parked`
* `PHASE7_SLICE=cmdline-runtime-leaf`
* `PHASE7_LANE_KEY=P7-Y06`
* scope: first low-risk runtime-safe parsing helpers only
* lane state: the slice note, dedicated test, dedicated survey, and committed manifest packet remain visible on current `master`, but direct current reads no longer prove `lib/cmdline.zig` or `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`; treat the cmdline packet as review-drifted until that helper-plus-fixture pair is restored or the remaining packet surfaces are rewritten to a blocked posture
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

Current repo reality is narrower than the parked packet summary above: on `2026-05-12`, direct current `master` reads still returned this slice note together with `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_cmdline_manifest.json`, but the same read path returned `404` for `lib/cmdline.zig` and `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`.
Treat the surviving note, test, survey, and manifest as a partial review record, not as proof that the bounded helper packet is fully landed today.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under this slice, `Documentation/zigux/README.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/cmdline.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting cmdline as a fifth Phase 5 sample.

## Gates

1. keep the surviving review record explicit

* `Documentation/zigux/phase7-cmdline-slice.md`
* `zigux/tests/phase7_cmdline.zig`
* `zigux/tests/phase7_cmdline_survey.zig`
* `zigux/tests/phase7_cmdline_manifest.json`

2. keep the missing helper-plus-fixture pair explicit as the current blocker

* `lib/cmdline.zig`
* `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`

3. keep the dedicated cmdline survey gate tied to that helper-plus-fixture pair instead of overstating current replayability

* `zigux/tests/phase7_cmdline_survey.zig`
* `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7-cmdline-survey`

4. keep the machine-readable review record explicit

* `zigux/tests/phase7_cmdline_manifest.json`

5. keep the shared validator-first packet explicit

* `python3 scripts/zigux/validate-phase7.py`
* `python3 scripts/zigux/check-phase7-make-wrapper.py`
* `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
* `python3 scripts/zigux/check-phase7-build-wiring.py`
* `make -C zigux phase7-validate`

6. keep the shared Phase 7 helper gate explicit once the helper-plus-fixture pair is visible again

* `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7-test`
* `make -C zigux phase7`

## Current Repo Reality

Current `master` still exposes a partial cmdline review packet:

* `Documentation/zigux/phase7-cmdline-slice.md`
* `zigux/tests/phase7_cmdline.zig`
* `zigux/tests/phase7_cmdline_survey.zig`
* `zigux/tests/phase7_cmdline_manifest.json`

Current `master` does not presently expose the full helper packet:

* `lib/cmdline.zig` currently fails direct current-path reads
* `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` currently fails direct current-path reads

That means the dedicated survey and dedicated helper test still describe the intended bounded packet, but they do not currently prove a replayable cmdline helper lane on their own.
The survey source still names the missing fixture module, and the survey body still reads `lib/cmdline.zig`, so the surviving review surfaces should be treated as drifted until the missing helper-plus-fixture pair returns or the surrounding packet is rewritten to a blocked posture.

The surviving review text and tests still document these intended packet edges:

* `getOption()` and `getOptions()` preserve Linux-style range parsing, including validator-only counting paths
* `getOption()` clears caller-provided output on malformed signed and unsigned input so the bounded helper packet keeps that failure contract explicit instead of leaving stale caller state behind
* `getOption()` and `getOptions()` keep the oversized wrap contract explicit across both 32-bit boundary inputs and full-width unsigned parses: `2147483648` wraps to `-2147483648`, `-2147483649` wraps to `2147483647`, `18446744073709551615` wraps to `-1`, `-18446744073709551615` wraps to `1`, and the paired `getOptions()` replays preserve the same wrapped values together with the validation-only count path
* `memparse()` preserves suffix scaling, leading plus handling, and stop-index reporting
* exact bare-option matching for comma-delimited flags stays reviewable through `parseOptionStr()`
* caller-owned `nextArg()` buffer slicing stays explicit for `param`, `value`, and `rest`
* empty-input handling keeps `param` and `rest` borrowed from the caller slice
* leading-whitespace handling keeps the Linux-style empty sentinel token
* the dedicated survey gate, the dedicated `phase7-cmdline-survey` compile-check replay, the committed manifest packet, the missing serialized fixture packet, the shared validator-first packet, the parked make-wrapper alignment note, and the no-sample boundary note are all still supposed to describe one bounded cmdline lane rather than separate ad hoc reminders

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

Stay in this cmdline lane and do one of two bounded things on a fresh `master` base:

* restore `lib/cmdline.zig` together with `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` so the surviving dedicated test, survey, manifest, and shared Phase 7 routes become replayable again
* or, if that helper-plus-fixture pair is not meant to ship on current `master`, rewrite the remaining cmdline-local review packet so it explicitly records the blocked state instead of reading like a fully landed helper slice

Do not widen this follow-through into broader Phase 7 helper-family cleanup until the cmdline-local helper-versus-review drift is settled.

## Footer
