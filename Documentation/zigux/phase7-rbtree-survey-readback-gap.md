# Phase 7 Rbtree Survey Readback Gap

## Scope

This note records one bounded Phase 7 repo-reality gap inside the runtime-safe leaf-helper family anchored on `lib/rbtree.zig`.

It does not reopen helper semantics, pointer ownership, balancing behavior, or broader Phase 7 expansion work.

## Why This Exists

The Phase 7 roadmap still calls for runtime-safe leaf helpers with stronger ownership discipline and validation-backed integration across:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

Current `master` still exposes the live `lib/rbtree.zig` helper and `zigux/tests/phase7_rbtree_survey.zig` survey gate, but direct readback in this environment shows a narrower mismatch:

- `zigux/tests/phase7_rbtree_survey.zig` still names a broader landed packet that includes `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-helper-lane-sequencing.md`, `zigux/tests/phase7_build.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, and fixture companions under `zigux/tests/fixtures/`.
- `Documentation/zigux/README.md` still describes a shared Phase 7 lane with slice notes and a `phase7_build.zig` gate for the string-helpers, cmdline, argv-split, and rbtree bundle.
- direct readback for those companion files currently returns missing contents instead of a landed Phase 7 packet.

That makes the current issue a validation-truthfulness gap, not a helper-behavior gap.

## Bounded Decision

Treat the current Phase 7 rbtree packet as:

- present helper anchor: `lib/rbtree.zig`
- present survey anchor: `zigux/tests/phase7_rbtree_survey.zig`
- present shared-summary anchor: `Documentation/zigux/README.md`
- missing companion packet: the broader Phase 7 docs, build, test, validator, and fixture surfaces still named by those summary anchors

The right short step is to guard that mismatch explicitly until the broader packet is either materialized or the summary language is narrowed.

## Checker Contract

`scripts/zigux/check-phase7-rbtree-survey-readback-gap.py` is the bounded checker for this note.

It should fail closed when:

- the current summary anchors stop naming the gap and this note needs retirement or refresh
- one of the currently missing companion files lands and this note is no longer accurate
- the live helper or survey anchors disappear and the gap changes shape

## Validation

This run validated the checker locally with:

- `python3 -m py_compile scripts/zigux/check-phase7-rbtree-survey-readback-gap.py`
- `python3 scripts/zigux/check-phase7-rbtree-survey-readback-gap.py --self-test`
