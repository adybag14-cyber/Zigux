# Phase 7 Argv Split Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/argv_split.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=argv-split-runtime-leaf`
- `PHASE7_LANE_KEY=P7-Y07`
- scope: first low-risk argv tokenization helpers only
- lane state: helper, fixture, survey, manifest, shared validator, dedicated packet checker, shared build-wiring checker, and make-wrapper slice landed; parked unless a new `argv_split.c` parity issue appears
- product boundary:
  - `lib/argv_split.zig`
  - `samples/zigux/README.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/check-phase7-build-wiring.py`
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
- stronger ownership and pointer discipline through the explicit `argvSplitWithArgc()` count mirror, `cArgv()` export, and `argvFree()` / `deinit()` teardown path
- helper-local owned-storage handoff reviewability through the internal `argvSplitOwnedStorage()` path, including blank owned-storage fallback to the canonical empty storage and exported argv sentinels
- integration with the parked shared Phase 7 validator-first, review-checklist, and make-wrapper control packet through `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, and `make -C zigux phase7`

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.

The Phase 5 roadmap keeps approved reference idioms under four sample anchors in `samples/zigux/`, and no `samples/zigux/*argv*` Phase 5 reference sample is expected here; keep `argv_split` reviewability under this slice, `samples/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `scripts/zigux/README.md`, `lib/argv_split.zig`, `zigux/tests/README.md`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig` instead of silently folding it into a fifth Phase 5 sample or leaving those already-landed sibling review surfaces implicit.

## Gates

1. run the focused Zig module tests
- `zig test lib/argv_split.zig`

2. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

3. run the dedicated manifest-backed Phase 7 survey gate from `repo_root`
- `zig test zigux/tests/phase7_argv_split_survey.zig`
- `make -C zigux phase7-argv-split-survey`

4. keep the dedicated packet surface machine-checked
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`

5. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`
- `make -C zigux phase7-validate`

6. keep the shared Linux-style replay route explicit
- `make -C zigux phase7`

## Current parity surface

The current landed slice covers:

- `countArgc()`
- `argvSplit()`
- `argvSplitWithArgc()`
- `cArgv()`
- `argvFree()` plus `deinit()`

The current tests check:

- repeated-whitespace collapsing into distinct argv entries
- blank-input handling
- first-NUL stop behavior for both `count_argc()` and `argv_split()`
- strict non-goal behavior where quote characters stay inside the returned tokens
- null-terminated pointer-vector access through `cArgv()`
- exported C-argv vector sizing to `argc + 1` so the trailing null sentinel stays aligned with `argvSplitWithArgc()` and `cArgv()`
- copied-buffer ownership so later source mutation does not affect split results
- copied whitespace separator runs are zeroed across the owned storage copy so each exported token stays in-place NUL-terminated
- caller-owned owned-storage reuse keeps token pointers inside the supplied storage copy, and blank owned-storage input falls back to the shared empty storage and exported argv sentinels without inventing extra allocator-backed state
- separate non-blank callers keep owned storage, argv slices, and exported C-argv views distinct across results
- tearing down one non-blank result does not disturb another caller's owned storage or exported C-argv view, whether teardown happens through `argvFree()` or `deinit()`
- blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`
- blank-input teardown on one caller keeps the shared empty storage and exported argv sentinels stable for another caller through both `argvFree()` and `deinit()`
- exported storage and argv views resetting back to the canonical empty sentinels after teardown
- allocator-failure cleanup when intermediate setup work is interrupted
- overflow rejection before sizing the exported null-terminated argv vector

The dedicated Phase 7 survey gate now imports the committed manifest under `zigux/tests/phase7_argv_split_manifest.json`, while the dedicated packet checker keeps that survey, the slice note, the focused fixture module under `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and the helper test entrypoint aligned. The shared `Documentation/zigux/review-checklist.md` note plus `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `validate-phase7.py`, `check-phase7-make-wrapper.py`, `check-phase7-make-wrapper-selftest-alignment.py`, `check-phase7-build-wiring.py`, `phase7_build.zig`, and `make -C zigux phase7-validate` plus `make -C zigux phase7` routes keep that same parked ownership-preserving packet reviewable through the validator-first, shared make-wrapper self-test, and Linux-style replay surfaces instead of leaving the shared Phase 7 packet implicit.

## Non-goals

This slice still does not yet claim:

- shell-style quote parsing
- escape-sequence processing
- a null-terminated pointer-vector API that mirrors the raw kernel allocation layout exactly
- generated C fixture parity artifacts

## Next bounded step

Keep this helper-family packet parked unless fresh repo inspection finds one more real `argv_split.c` parity gap inside the existing helper, fixture, dedicated survey, dedicated manifest, shared validator, dedicated packet checker, shared make-wrapper alignment note, or make-wrapper surface. Review-only sequencing drift for other Phase 7 helper families should stay outside this packet.
