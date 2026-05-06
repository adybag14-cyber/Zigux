# Phase 7 Argv Split Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/argv_split.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=argv-split-runtime-leaf`
- `PHASE7_LANE_KEY=P7-Y07`
- scope: first low-risk argv tokenization helpers only
- lane state: helper, fixture, survey, manifest, shared validator, dedicated packet checker, and make-wrapper slice landed; parked unless a new `argv_split.c` parity issue appears
- product boundary:
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-argv-split-packet.py`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 7 explicitly calls out `lib/argv_split.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to the smallest runtime-safe ownership-preserving surface:

- whitespace-only argv tokenization
- first-NUL C-string bounds on both counting and splitting
- an explicit result object that owns the copied token buffer
- deterministic Zig-only validation without quote or shell expansion behavior

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

The Phase 5 roadmap keeps approved reference idioms under four sample anchors in `samples/zigux/`, and no `samples/zigux/*argv*` Phase 5 reference sample is expected here; treat any new `samples/zigux/*argv*.zig` claim as a separate roadmap-boundary decision instead of silently folding it into this helper slice.

## Gates

1. run the focused Zig module tests
- `zig test lib/argv_split.zig`

2. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig`

3. run the dedicated Phase 7 survey gate
- `zig test zigux/tests/phase7_argv_split_survey.zig`

4. keep the dedicated packet surface machine-checked
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`

5. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`
- `make -C zigux phase7-validate`

6. keep the shared Linux-style replay route explicit
- `make -C zigux phase7`

## Current parity surface

The current landed slice covers:

- `count_argc()`
- `argv_split()`

The current tests check:

- repeated-whitespace collapsing into distinct argv entries
- blank-input handling
- first-NUL stop behavior for both `count_argc()` and `argv_split()`
- strict non-goal behavior where quote characters stay inside the returned tokens
- null-terminated pointer-vector access through `cArgv()`
- copied-buffer ownership so later source mutation does not affect split results
- blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`
- exported storage and argv views resetting back to the canonical empty sentinels after teardown

The dedicated Phase 7 survey gate now imports the committed manifest under `zigux/tests/phase7_argv_split_manifest.json`, while the dedicated packet checker keeps that survey, the slice note, the focused fixture module under `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and the helper test entrypoint aligned. The shared `validate-phase7.py`, `phase7_build.zig`, `zigux/Makefile`, and `make -C zigux phase7-validate` plus `make -C zigux phase7` routes keep that same parked ownership-preserving packet reviewable through the validator-first and Linux-style replay surfaces instead of leaving the shared Phase 7 packet implicit.

## Non-goals

This slice still does not yet claim:

- shell-style quote parsing
- escape-sequence processing
- a null-terminated pointer-vector API that mirrors the raw kernel allocation layout exactly
- generated C fixture parity artifacts

## Next bounded step

Keep this helper-family packet parked unless fresh repo inspection finds one more real `argv_split.c` parity gap inside the existing helper, fixture, dedicated survey, dedicated manifest, shared validator, dedicated packet checker, or make-wrapper surface. Review-only sequencing drift for other Phase 7 helper families should stay outside this packet.
