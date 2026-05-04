# Phase 7 Argv Split Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/argv_split.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=argv-split-runtime-leaf`
- scope: first low-risk argv tokenization helpers only
- lane state: helper, fixture, survey, and dedicated external parity slice landed; parked unless a new `argv_split.c` parity issue appears
- product boundary:
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `zigux/tests/fixtures/phase7_argv_split.json`
  - `zigux/tests/fixtures/phase7_argv_split_c_harness.c`
  - `scripts/zigux/check-phase7-argv-split-packet.py`
  - `scripts/zigux/check-phase7-argv-split-parity.py`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/argv_split.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe leaf helpers with explicit shared integration through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, and `zigux/tests/phase7_build.zig`.

The dedicated packet-alignment replay through `scripts/zigux/check-phase7-argv-split-packet.py` and the committed C parity replay through `scripts/zigux/check-phase7-argv-split-parity.py` stay adjacent to that shared validation substrate so the helper-only slice remains externally reviewable without widening into new helper behavior or broader Phase 7 scope.

That dedicated packet checker now also fails closed on the landed docs-root, scripts-root, and tests-root review markers, so the shared reviewer guides around `zigux/tests/README.md` stay part of the same bounded argv_split ownership packet instead of drifting behind the helper and fixture evidence.

This current slice keeps the work bounded to the smallest runtime-safe ownership-preserving surface:

- whitespace-only argv tokenization
- first-NUL C-string bounds on both counting and splitting
- optional argc reporting that matches the C helper's out-parameter shape more directly
- explicit `argv_free()` release parity via `argvFree()`
- an explicit result object that owns the copied token buffer
- a shared exported empty argv view for blank input without extra argv-vector allocation
- deterministic Zig-only validation without quote or shell expansion behavior

## Gates

1. prove the shared Phase 7 validator packet plus the build-inventory, make-wrapper, argv_split packet-alignment, and argv_split parity gates still fail closed before the helper replay runs
- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase7-build-inventory.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`
- `python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-parity.py`
- `make -C zigux phase7-validate`

2. run the focused Zig module tests
- `zig test lib/argv_split.zig`

3. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

4. keep the helper wired through the Zigux convenience target
- `make -C zigux phase7`

5. keep the roadmap survey record machine-checked from `repo_root`
- `zig test zigux/tests/phase7_argv_split_survey.zig`

6. keep the dedicated direct parity replay callable on its own too
- `python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-parity.py`

7. keep the dedicated packet-alignment replay callable on its own too
- `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`

## Current parity surface

The current landed slice covers:

- `count_argc()`
- `argv_split()`
- optional `argcp` reporting through `argvSplitWithArgc()`
- `argv_free()` via `argvFree()`

The current tests check:

- repeated-whitespace collapsing into distinct argv entries
- blank-input handling
- leading-NUL truncation to zero argv entries before any later bytes are considered
- first-NUL stop behavior for both `count_argc()` and `argv_split()`
- strict non-goal behavior where quote characters stay inside the returned tokens
- null-terminated pointer-vector access through `cArgv()`
- copied-buffer ownership so later source mutation does not affect split results
- optional argc reporting that stays in sync with the returned argv length
- the explicit `argv_free()` ownership mirror through `argvFree()` over an already-split result object
- blank-input reuse of the exported empty argv view under a four-byte fixed-buffer allocator, including pointer-stable reuse across repeated empty-result calls
- repeated blank-input `argvFree()` teardown safety so the shared empty sentinel state survives explicit release without allocator backing
- teardown cleanup that clears the exported storage handle alongside the argv views after `ArgvSplitResult.deinit()`
- blank-input reuse of the exported empty storage sentinel without allocator backing, including pointer-stable reuse across repeated empty-result calls
- repeated teardown safety so an already-cleared `ArgvSplitResult` can be passed through `deinit()` again without freeing the shared empty sentinel state
- allocator-failure cleanup that proves the shared Phase 7 gate also exercises the intermediate allocation teardown path already covered by the direct helper tests
- a machine-checked survey record that keeps the Phase 7 roadmap anchor and landed review surfaces explicit without advertising active same-lane work
- committed C-vs-Zig parity for whitespace collapse, blank input, first-NUL stop behavior, leading-NUL truncation, and the quote-literal non-goal through `zigux/tests/fixtures/phase7_argv_split.json` plus `zigux/tests/fixtures/phase7_argv_split_c_harness.c`

The dedicated Phase 7 review gate now imports a focused fixture module under `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, while the helper self-tests keep the same bounded parity surface local to `lib/argv_split.zig`.

The manifest-backed survey packet stays rooted at `repo_root` through `zigux/tests/phase7_build.zig` so `zigux/tests/phase7_argv_split_manifest.json` remains a reviewable ownership record instead of a helper-local detail.

The shared Phase 7 validator packet plus the build-inventory, make-wrapper, and argv_split parity replays stay in that same review packet, while the dedicated packet-alignment checker remains a separate callable lane-local replay, so the committed `zigux/tests/fixtures/phase7_build_inventory.json` snapshot, the published `make -C zigux phase7-validate` wrapper path, the focused C parity fixture lane, the dedicated packet-alignment checker, and the one-command `make -C zigux phase7` bundle remain explicit instead of living only in the broader shared Phase 7 notes.

## Non-goals

This slice still does not yet claim:

- shell-style quote parsing
- escape-sequence processing
- a null-terminated pointer-vector API that mirrors the raw kernel allocation layout exactly

## Next bounded step

Move the next Phase 7 schedule to another unfinished leaf helper family. Reopen this lane only if fresh repo inspection finds one more real `argv_split.c` parity gap or one shared review-surface drift inside the existing helper, fixture, survey, dedicated-gate, build-inventory, or make-wrapper packet.
