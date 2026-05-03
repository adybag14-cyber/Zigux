# Phase 3 Rbtree Interop Survey

This note records the current state of the roadmap-backed `lib/rbtree.c` anchor inside the live Phase 3 ABI and interop packet.

## Status

- `PHASE3_RBTREE_ROADMAP_ANCHOR=lib/rbtree.c`
- `PHASE3_RBTREE_PHASE1_EVIDENCE=tools/lib/rbtree.zig,Documentation/zigux/phase1-closure.md`
- `PHASE3_RBTREE_PHASE7_EVIDENCE=lib/rbtree.zig,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_RBTREE_PHASE3_HELPER=zigux/helpers/rbtree_view.zig,zigux/helpers/rbtree_root_view.zig`
- `PHASE3_RBTREE_PHASE3_BOUNDARY=include/zigux/rbtree.h,zigux/bindings/rbtree.zig,zigux/tests/phase3_rbtree_dump.zig,zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c`
- `PHASE3_RBTREE_PHASE3_SURVEY=zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_root_view_survey.zig,zigux/tests/phase3_rbtree_manifest.json`
- `PHASE3_RBTREE_PHASE3_SLICE=Documentation/zigux/phase3-rbtree-slice.md`
- `PHASE3_RBTREE_PHASE3_BOUNDARY_STATUS=dedicated-boundary-landed-shared-abi-lift-still-missing`
- `PHASE3_RBTREE_NON_GOALS=no-balancing-port,no-export-shim-growth,no-uapi-growth`
- `PHASE3_RBTREE_NEXT_BOUNDED_STEP=one-shared-phase3-abi-rbtree-root-view`
- `PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet`
- `PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid`
- `PHASE3_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig`
- `PHASE3_RBTREE_SHARED_PACKET_CATALOG=phase3_abi_manifest-catalogs-dedicated-rbtree-boundary-packet`
- `PHASE3_RBTREE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py`
- `PHASE3_RBTREE_SHARED_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_RBTREE_SHARED_MAKE_GATE=make -C zigux phase3-validate`

## Roadmap Anchor

Phase 3 names `lib/rbtree.c` as one of the four permanent C/Zigux boundary anchors. That means the remaining work here is not general helper growth. The remaining work is one reviewable Phase 3 packet that lifts the existing dedicated `rbtree` boundary into the shared ABI substrate.

## Current Evidence

The repo already carried real `rbtree` evidence in two later-adjacent packets:

- `tools/lib/rbtree.zig` plus `Documentation/zigux/phase1-closure.md` record the earlier host-helper parity lane
- `lib/rbtree.zig`, `Documentation/zigux/phase7-rbtree-slice.md`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` record the later runtime-helper lane

This Phase 3 lane now adds both the helper-local packet and a dedicated boundary packet on top of that evidence:

- `zigux/helpers/rbtree_view.zig` provides a bounded read-mostly summary over the existing runtime `rbtree` surface
- `zigux/helpers/rbtree_root_view.zig` now adds a reusable constructor and canonicalization helper around the dedicated `RootView` binding so later shared-packet work can reuse one explicit flag-policy path
- `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig` define a dedicated `rbtree` root view outside the shared ABI packet
- `zigux/tests/phase3_rbtree_dump.zig` plus `zigux/tests/fixtures/phase3_rbtree/expected.json` and `zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c` keep that dedicated boundary replayable across C and Zig
- `Documentation/zigux/phase3-rbtree-slice.md`, `zigux/tests/phase3_rbtree_survey.zig`, `zigux/tests/phase3_rbtree_root_view_survey.zig`, and `zigux/tests/phase3_rbtree_manifest.json` keep the landed helper packet machine-checked
- `zigux/tests/phase3_rbtree_shared_contract.zig` now keeps that planned shared packet layout and constant contract machine-checked even before the full shared header lift lands
- the shared Phase 3 ABI manifest now explicitly catalogs the dedicated `rbtree` boundary header, binding, dump, survey, and parity fixture files so the remaining gap is the shared header and binding lift itself rather than whether the dedicated packet belongs to the shared ABI tranche

That means the remaining Phase 3 gap is no longer “no curated C header, bindings record, or parity fixture exists.” The remaining gap is that current `master` still has no shared `rbtree` record inside `include/zigux/abi.h`, `zigux/bindings/abi.zig`, and the shared `phase3_abi` fixture packet.

## Validation Path

The live Phase 3 validation packet already exposes this survey through dedicated and shared gates:

- `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` keeps this dedicated survey note, the broader `Documentation/zigux/phase3-roadmap-gap-survey.md` note, and the repo-backed evidence paths aligned
- `python3 scripts/zigux/check-phase3-rbtree-shared-lift-contract.py` keeps the dedicated root-view layout, constants, and shared-lift note aligned before the shared ABI packet grows
- `python3 scripts/zigux/validate-phase3.py --slug abi` keeps that dedicated `rbtree` gap visible inside the shared Phase 3 ABI validation packet instead of leaving it as prose-only context
- `make -C zigux phase3-validate` remains the shared wrapper entrypoint for the broader bounded ABI packet, so this survey stays reviewable through the same published Phase 3 gate

## Missing Shared ABI Lift

Current `master` still lacks the direct shared Phase 3 ABI lift that would close this anchor:

- no curated `rbtree` record in `include/zigux/abi.h`
- no matching shared `zigux/bindings/abi.zig` layout type for a Phase 3 `rbtree` boundary packet
- no shared C-vs-Zig parity fixture for that `rbtree` root view inside `zigux/tests/fixtures/phase3_abi/`

## Non-Goals

This survey does not treat any of the following as the next honest Phase 3 step:

- porting the full balancing or mutation path from `lib/rbtree.c`
- widening `zigux/kernel/export_shim.zig` or `zigux/uapi/version.zig`
- counting the larger `chrdev_*` planning ladder as substitute closure for the roadmap-backed `rbtree` anchor

## Next Bounded Step

The next honest same-lane follow-on is one small shared Phase 3 `rbtree` ABI lift:

- one curated read-mostly ABI record in the shared packet
- one matching shared Zig binding shape
- one committed shared parity fixture that keeps the contract reviewable without widening into a full balancing port
- the shared lift should reuse the dedicated `zigux_rbtree_root_view` layout and `root_flag_empty`, `root_flag_cached`, and `root_flag_leftmost_valid` constants unchanged so the contract stays reviewable across the existing dedicated parity fixture
