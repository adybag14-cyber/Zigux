# Phase 7 Toolchain Validation Wrapper Gap

This note records the current Phase 7 wrapper reality on `master` so reminder surfaces stop treating older wrapper routes as shipped evidence.

## Roadmap anchor

Phase 7 is still the in-kernel leaf-library tranche.

- primary Linux anchors:
  - `lib/cmdline.c`
  - `lib/string_helpers.c`
  - `lib/argv_split.c`
  - `lib/rbtree.c`
- required Zigux features:
  - reusable runtime helper ports
  - reviewable validation surfaces
  - toolchain-backed wrapper evidence for helper replay
- recommended Zigux destinations:
  - `lib/string_helpers.zig`
  - `lib/cmdline.zig`
  - `lib/argv_split.zig`
  - `lib/rbtree.zig`

The roadmap still expects a helper tranche plus validation discipline. Repo reality now needs to stay explicit so older wrapper notes do not overclaim what current `master` ships.

## Live repo reality on current master

Current `master` still materializes a partial Phase 7 helper foothold.

- surviving helper roots:
  - `lib/cmdline.zig`
  - `lib/argv_split.zig`
  - `lib/string_helpers.zig`
- missing helper or wrapper companions from the earlier Phase 7 packet:
  - `lib/rbtree.zig`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `zigux/tests/phase7_build.zig`
  - `Documentation/zigux/phase7-cmdline-slice.md`
  - `Documentation/zigux/phase7-argv-split-slice.md`
- readable shared non-owner surface:
  - `zigux/Makefile`

The current `zigux/Makefile` no longer exposes `phase7`, `phase7-validate`, or `phase7-test`. Its live body currently carries only the rematerialized Phase 2 routes, the bounded `phase3-validate` and `phase3` routes, and the Phase 10 wrappers. That means old Phase 7 wrapper names should stay framed as repo-reality gaps until a fresh reread proves they returned.

## Regression-evidence rules

1. Keep the surviving helper roots explicit without treating them as proof that the old wrapper packet still ships.
2. Keep `zigux/Makefile` explicit as readable current-head evidence, but do not infer missing `phase7*` routes from the returned file.
3. Keep `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_build.zig`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, and `make -C zigux phase7`, `make -C zigux phase7-validate`, `make -C zigux phase7-test` framed as missing-current-master companions unless a fresh reread proves they returned.
4. Prefer one shared reminder repair at a time if Phase 7 reminder surfaces drift again.
5. Do not reopen helper semantics from stale wrapper wording alone.

## Recommended next step

If a future current-head reread finds the Phase 7 wrapper packet returning, compare the exact file family above first before widening into new helper or validation work. If the files stay absent, keep follow-up limited to shared reminder truthfulness instead of rebuilding the old wrapper story by implication.
