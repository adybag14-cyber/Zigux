# Phase 7 Build Entrypoint Evidence

This note records the current shared Phase 7 build graph entrypoints on `master` so review of the parked helper packet can rely on one compact evidence surface.

## Scope

This note is limited to the shipped build and validation routes for the existing Phase 7 helper packet:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`
- `zigux/tests/phase7_build.zig`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/check-phase7-make-wrapper.py`
- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `scripts/zigux/check-phase7-argv-split-packet.py`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `zigux/Makefile`

It does not reopen helper semantics, wrapper ownership, or Phase 5 sample-boundary claims.

## Shared Validation Route

The current Linux-style validation entrypoint is:

- `make -C zigux phase7-validate`

That route keeps the shared validator and the dedicated helper-packet checkers together:

- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`
- `python3 scripts/zigux/check-phase7-build-wiring.py`

## Shared Test Route

The current direct summarized replay is:

- `make -C zigux phase7-test`
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

The current aggregate route remains:

- `make -C zigux phase7`

That route keeps validation-first replay discipline by running `phase7-validate` before `phase7-test`.

## Dedicated Survey Entrypoints

The current helper-local survey and boundary replays exposed through `zigux/Makefile` are:

- `make -C zigux phase7-string-helpers-survey`
- `make -C zigux phase7-string-helpers-sample-boundary`
- `make -C zigux phase7-cmdline-survey`
- `make -C zigux phase7-argv-split-survey`
- `make -C zigux phase7-rbtree-survey`

Those map to dedicated `zig build ... --build-file zigux/tests/phase7_build.zig --summary all` replays rather than ad hoc helper-local wrappers.

## Reviewability Claim

Current Phase 7 build-graph evidence on `master` is therefore:

- one shared build file for the parked helper family
- one shared validator-first make route
- one shared summarized test route
- five dedicated survey or sample-boundary make entrypoints for focused replay
- one dedicated build-wiring checker that keeps the shared build-step packet reviewable

This note exists so later Phase 7 reminder, checklist, or scripts-index edits can verify those exact entrypoints without drifting back toward older unshipped build-inventory stories.
