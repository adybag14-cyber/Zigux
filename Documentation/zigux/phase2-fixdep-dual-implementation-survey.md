# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

This note records the current `master` readback for the roadmap-backed `fixdep` lane so Phase 2 review stays grounded in the live tree instead of in the older snapshot-backed packet.

## Roadmap target

- Phase 2 keeps `scripts/basic/fixdep.c` inside the bounded toolchain tranche.
- The roadmap requires selected dual implementations, and the recommended Zigux destination is `scripts/zigux/fixdep.zig`.
- The bootstrap ledger records a bounded fixdep lane with the Zig replay, a diff checker, a dedicated gate, committed fixtures, and a workflow-backed validation route.

## Current master readback

- Shared Phase 2 reminder surfaces still name a shipped fixdep packet from `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md`.
- Direct current-`master` contents reads return missing for:
  - `scripts/zigux/fixdep.zig`
  - `scripts/zigux/check-fixdep-diff.py`
  - `scripts/zigux/check-phase2-fixdep-gate.py`
  - `scripts/zigux/validate-phase2.py`
  - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  - `Documentation/zigux/phase2-closure.md`
  - `scripts/basic/fixdep.c`
  - `scripts/include/xalloc.h`
  - `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml` still watches `scripts/basic/fixdep.c`, `scripts/include/xalloc.h`, and `scripts/zigux/**`, so the lane is still structurally expected even though the fixdep packet itself is absent on live `master`.
- The attached `Zigux-master.zip` snapshot still carries a bounded fixdep packet, including `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/basic/fixdep.c`, `scripts/include/xalloc.h`, and the `zigux/tests/fixtures/fixdep/` artifact set.
- Local snapshot validation confirmed the saved Zig replay is still viable with the attached Zig toolchain:
  - `zig test scripts/zigux/fixdep.zig`
  - `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`

## Survey result

- Current `master` has a real Lane 11 repo-reality gap: the shared Phase 2 reminder surfaces still talk as if the bounded fixdep dual-implementation packet is present, but the packet itself is absent from the live tree.
- The honest next step is smaller than broad Phase 2 closure churn and larger than another reminder-only restatement: restore the fixdep-local implementation pair and bounded checker or fixture packet first, then revisit the shared Phase 2 surfaces after those files exist again.

## Next bounded step

1. Restore `scripts/basic/fixdep.c`, `scripts/include/xalloc.h`, and `scripts/zigux/fixdep.zig` as the smallest live implementation pair for the lane.
2. Add back the fixdep-local checker and fixture packet next: `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `zigux/tests/fixtures/fixdep/`.
3. Re-run `zig test scripts/zigux/fixdep.zig` plus the fixdep-local checker self-tests before treating the shared Phase 2 README, tests-root, closure, Makefile, or workflow wording as current direct evidence again.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `genksyms`, the kconfig bridge packet, or broader shared Phase 2 closure wording unless a later fixdep-local restore proves one of those surfaces directly wrong.