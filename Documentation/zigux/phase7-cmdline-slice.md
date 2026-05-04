# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=cmdline-runtime-leaf`
- scope: first low-risk parsing helpers only
- lane state: helper, fixture, and parity-adapter slice landed; parked unless a new `cmdline.c` parity issue appears
- product boundary:
  - `lib/cmdline.zig`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_cmdline_survey.zig`
  - `zigux/tests/phase7_cmdline_manifest.json`
  - `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
  - `zigux/tests/fixtures/phase7_cmdline.json`
  - `zigux/tests/fixtures/phase7_cmdline_c_harness.c`
  - `scripts/zigux/check-phase7-cmdline-parity.py`
  - `zigux/tests/phase7_build.zig`

## Why this slice exists

Phase 7 explicitly calls out `lib/cmdline.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to runtime-safe leaf helpers with explicit integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig`.

The committed C parity replay through `scripts/zigux/check-phase7-cmdline-parity.py` stays coupled to that validation substrate so the helper-only slice remains externally reviewable.

The manifest-backed survey packet stays rooted at `repo_root` through `zigux/tests/phase7_build.zig` so `zigux/tests/phase7_cmdline_manifest.json` remains a reviewable ownership record instead of a helper-local detail.

This current slice therefore stays inside helpers that:

- do not allocate
- keep deterministic parsing and cursor-advance behavior reviewable across helper-local, external parity, and shared Phase 7 gates

## Gates

1. prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs
- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase7-build-inventory.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `make -C zigux phase7-validate`

2. run the focused Zig module tests
- `zig test lib/cmdline.zig`

3. run the shared Phase 7 helper gate
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

4. keep the helper wired through the Zigux convenience target
- `make -C zigux phase7`

5. keep the manifest-backed survey record machine-checked from `repo_root`
- `zig test zigux/tests/phase7_cmdline_survey.zig`

6. check the committed C parity fixture and its dedicated checker self-test
- `python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test`
- `python3 scripts/zigux/check-phase7-cmdline-parity.py`

The shared Phase 7 validator packet plus the build-inventory, make-wrapper, and dedicated cmdline parity self-tests stay the published fail-closed handoff before helper replay, while the committed cmdline parity fixture keeps the narrower helper surface externally reviewable.

The shared build-inventory gate and published `make -C zigux phase7` convenience path stay in that same review packet, so the committed `zigux/tests/fixtures/phase7_build_inventory.json` snapshot and the one-command wrapper route remain explicit instead of living only in the broader shared Phase 7 notes.

## Current parity surface

The current landed slice covers:

- `get_option()`
- `get_options()`
- `memparse()`
- `parse_option_str()`
- `next_arg()`

The current tests check:

- committed C-vs-Zig parity for representative `get_option()`, `get_options()`, `memparse()`, `parse_option_str()`, and `next_arg()` cases through `zigux/tests/fixtures/phase7_cmdline.json` plus `zigux/tests/fixtures/phase7_cmdline_c_harness.c`
- signed integer parsing and comma handling
- Linux-style hyphen range expansion and validation-only counting
- descending-range and unparseable-suffix early stop behavior
- array-capacity stop behavior when a hyphen range is only partially stored and the upper bound remains pending in the remaining cursor
- malformed token classification and malformed range counting ported from the in-tree `lib/tests/cmdline_kunit.c` corpus
- the full KUnit malformed-token classification corpus now also runs through the shared `zigux/tests/phase7_cmdline.zig` gate instead of only the helper-local `zig test lib/cmdline.zig` path
- KUnit-derived pointer-advance semantics for malformed-prefix, leading-integer, and trailing-integer `get_option()` inputs so the shared Phase 7 gate and the helper-local test path both keep matching where the C helper leaves the parse cursor
- memory-size suffix scaling with accurate parse-stop reporting
- rejection of explicit leading-plus numeric inputs, including autodetected radix forms like `+0x10`, so the Zig helper stays aligned with the `lib/cmdline.c` `simple_strtoull()` parsing contract
- exact bare-option matching for comma-delimited flags
- C-style stop-at-NUL handling for bare-option scans
- committed C-vs-Zig parity for `parse_option_str()` now keeps that stop-at-NUL scan behavior in the checked JSON fixture instead of leaving it helper-local only
- `parse_option_str()` empty-needle parity now mirrors the live C helper: empty option names only match empty segments at the start of the scan or between commas, while an empty source string or a purely trailing comma still return false
- serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, trailing-space trimming after `key=value`, and empty-rest termination
- helper-local `next_arg()` ownership proof that `param`, optional `value`, and `rest` remain slices into the caller-owned mutable buffer while the helper rewrites only the split `=`, closing quote, and token delimiter bytes to NUL in place
- the dedicated C parity fixture now also keeps quoted bare-token ownership and first-equals value splitting externally reviewable instead of leaving those edges only in the helper-local and shared Zig packets
- a machine-checked manifest that records the `lib/cmdline.c` anchor and the landed Phase 7 review surfaces

Review note:
- this slice intentionally follows `lib/cmdline.c` and its `simple_strtoull()` call sites, not the broader `kstrtoull()` family in `lib/kstrtox.c` that does accept a leading `+`
- `zig test lib/cmdline.zig` keeps a mirrored `next_arg()` edge corpus beside `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` because helper-local test runs cannot import that fixture from outside the helper module path; keep both packets aligned when those serialized cases change
- `next_arg()` is intentionally in-place: it returns slices into the caller-owned mutable buffer and rewrites only the bytes used as the split `=`, closing quote, and token delimiter when it terminates `param`, `value`, and `rest`
- the shared build-inventory gate stays part of this parked review packet, so `zigux/tests/fixtures/phase7_build_inventory.json` plus the published `make -C zigux phase7-validate` wrapper path stay explicit instead of living only in the broader shared Phase 7 notes

## Non-goals

This slice still does not yet claim:

- exhaustive overflow compatibility with every `simple_strtoull()` corner case
- broader parameter-name normalization or cross-subsystem callers beyond the local helper surface

## Next bounded step

Move the next Phase 7 schedule to another unfinished leaf helper family. Reopen this lane only if fresh repo inspection finds one more real `cmdline.c` parity gap inside the existing helper, fixture, dedicated-gate, or external-parity surface.
