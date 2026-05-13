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
  * `Documentation/zigux/phase7-helper-lane-sequencing.md`
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
* shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`; keep that shared route framed as a cross-packet review surface rather than a fresh cmdline-local green claim unless the full shared replay is rerun

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe parsing helpers that:

- do not allocate
- do not widen into shell, process, runtime-loader, or sample-owned execution behavior
- keep range parsing, suffix-aware size parsing, exact bare-option matching for comma-delimited flags, and `nextArg()` token splitting reviewable through deterministic Zig replays
- keep empty-input handling keeps `param` and `rest` borrowed from the caller slice
- keep leading-whitespace handling keeps the Linux-style empty sentinel token
- keep mixed-whitespace trimming and caller-owned buffer slicing explicit instead of widening into ownership-heavy follow-on helpers

Current repo reality is narrower only at the helper-local verification level: on `2026-05-13`, direct current `master` reads returned this slice note together with `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, and the shared `zigux/tests/phase7_build.zig` route.
That means the cmdline-local helper packet is still landed, while the broader shared `phase7_build.zig` replay remains a shared cross-packet review surface rather than a fresh cmdline-local green claim from this note alone.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under this slice, `Documentation/zigux/README.md`, `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/cmdline.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting cmdline as a fifth Phase 5 sample.

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

5. keep the shared Phase 7 helper gate explicit as a shared cross-packet route

The commands below still describe the shared replay surface that current `master` exposes through direct readback, but they are not a fresh cmdline-local green claim from this slice note alone until that full bundle replay is rerun.

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

Current `master` also keeps the shared Phase 7 helper route directly readable:

* `zigux/tests/phase7_build.zig`
* `lib/string_helpers.zig`
* `zigux/tests/phase7_string_helpers.zig`
* `lib/argv_split.zig`
* `zigux/tests/phase7_argv_split.zig`
* `lib/rbtree.zig`
* `zigux/tests/phase7_rbtree.zig`

That means the dedicated cmdline helper replay and dedicated cmdline survey remain reviewable inside this slice, while the broader shared `phase7_build.zig` route is again a present shared replay surface on `master` rather than a missing-sibling blocker.
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
* serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination stay reviewable through `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
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
Treat any fresh shared `phase7_build.zig` replay claim as a cross-packet follow-through that should be backed by a new direct shared replay, not just by current-master readback.

## Footer
