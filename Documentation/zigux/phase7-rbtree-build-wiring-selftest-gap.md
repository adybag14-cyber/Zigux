## Phase 7 rbtree build-wiring self-test gap

Date: 2026-05-16
Lane: `p7-kernel-leaf-libs`
Slot: `355 22:02 BST`

### Why this is still a valid bounded Phase 7 task

The Phase 7 roadmap keeps this lane inside runtime-safe leaf helpers and validation discipline for `string_helpers`, `cmdline`, `argv_split`, and `rbtree`. Fresh repo-first inspection of current `master` showed the live `rbtree` parity checker has already moved to the newer shared build-wiring packet, but the checker's own self-test surface still trails that reality.

That makes the smallest honest same-lane improvement a validation-gap artifact rather than another helper expansion or a blind whole-file rewrite of the live checker.

### Live repo evidence inspected

- `Documentation/zigux/phase7-rbtree-slice.md` currently lists `scripts\zigux/check_phase7_build_wiring.zig` inside the active Phase 7 rbtree product boundary.
- `scripts\zigux/validate_phase7.zig` currently lists both `zig run scripts/zigux/check_phase7_rbtree_parity.zig -- --self-test` and `zig run scripts/zigux/check_phase7_build_wiring.zig -- --self-test` inside the shared Phase 7 validation packet.
- `scripts\zigux/check_phase7_rbtree_parity.zig` currently exact-requires `scripts\zigux/check_phase7_build_wiring.zig` from the surrounding review packet.
- the same `check-phase7-rbtree-parity.py` self-test block still shows a narrower `missing_file_cases` list whose visible entries stop at:
  - `missing_manifest`
  - `missing_json_fixture`
  - `missing_c_harness`
- that visible self-test list does not currently include a missing-file branch for `scripts\zigux/check_phase7_build_wiring.zig`, even though the checker now depends on that surface.

### Safest bounded repair when the checker body is writable

Preferred one-file follow-up:

1. update `scripts\zigux/check_phase7_rbtree_parity.zig`
2. add one missing-file self-test branch for `scripts\zigux/check_phase7_build_wiring.zig`
3. bump `PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT` accordingly
4. keep the change scoped to the checker self-test only

### Why this run stopped at a note plus checker

This runtime could inspect the live repo through GitHub and public blob reads, but it could not materialize a byte-faithful writable checkout of current `master`. Whole-file replacement without a trustworthy full read would risk dropping unrelated checker content.

The bounded note plus checker below keeps the real gap explicit and machine-checkable until a safer direct edit path is available.
