# Phase 3 Rbtree Interop Survey

This note records the current state of the roadmap-backed `lib/rbtree.c` anchor inside the live Phase 3 ABI and interop packet.

## Status

- `PHASE3_RBTREE_ROADMAP_ANCHOR=lib/rbtree.c`
- `PHASE3_RBTREE_PHASE1_EVIDENCE=tools/lib/rbtree.zig,Documentation/zigux/phase1-closure.md`
- `PHASE3_RBTREE_PHASE7_EVIDENCE=lib/rbtree.zig,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_RBTREE_PHASE3_HELPER=zigux/helpers/rbtree_view.zig`
- `PHASE3_RBTREE_PHASE3_SURVEY=zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_manifest.json`
- `PHASE3_RBTREE_PHASE3_SLICE=Documentation/zigux/phase3-rbtree-slice.md`
- `PHASE3_RBTREE_PHASE3_BOUNDARY=helper-landed-curated-c-binding-surface-still-missing`
- `PHASE3_RBTREE_NON_GOALS=no-balancing-port,no-export-shim-growth,no-uapi-growth`
- `PHASE3_RBTREE_NEXT_BOUNDED_STEP=one-curated-phase3-rbtree-boundary-record`
- `PHASE3_RBTREE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py`
- `PHASE3_RBTREE_SHARED_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_RBTREE_SHARED_MAKE_GATE=make -C zigux phase3-validate`

## Roadmap Anchor

Phase 3 names `lib/rbtree.c` as one of the four permanent C/Zigux boundary anchors. That means the remaining work here is not general helper growth. The remaining work is one reviewable Phase 3 packet that turns existing `rbtree` evidence into a boundary-facing interop slice.

## Current Evidence

The repo already carried real `rbtree` evidence in two later-adjacent packets:

- `tools/lib/rbtree.zig` plus `Documentation/zigux/phase1-closure.md` record the earlier host-helper parity lane
- `lib/rbtree.zig`, `Documentation/zigux/phase7-rbtree-slice.md`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` record the later runtime-helper lane

This lane adds the missing first Phase 3 helper packet on top of that evidence:

- `zigux/helpers/rbtree_view.zig` provides a bounded read-mostly summary over the existing runtime `rbtree` surface
- `Documentation/zigux/phase3-rbtree-slice.md` records the helper-local boundary and the still-missing follow-on contract
- `zigux/tests/phase3_rbtree_survey.zig` plus `zigux/tests/phase3_rbtree_manifest.json` keep the helper packet machine-checked

That means the remaining Phase 3 gap is no longer “no helper exists.” The remaining gap is that current `master` still has no curated C header, bindings record, or parity fixture for a boundary-facing `rbtree` packet.

## Validation Path

The live Phase 3 validation packet already exposes this survey through dedicated and shared gates:

- `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` keeps this dedicated survey note, the broader `Documentation/zigux/phase3-roadmap-gap-survey.md` note, and the repo-backed evidence paths aligned
- `python3 scripts/zigux/validate-phase3.py --slug abi` keeps that dedicated `rbtree` gap visible inside the shared Phase 3 ABI validation packet instead of leaving it as prose-only context
- `make -C zigux phase3-validate` remains the shared wrapper entrypoint for the broader bounded ABI packet, so this survey stays reviewable through the same published Phase 3 gate

## Missing Boundary Contract

Current `master` still lacks the direct Phase 3 boundary contract that would close this anchor:

- no curated `rbtree` record in `include/zigux/abi.h`
- no matching `zigux/bindings/abi.zig` layout type for a Phase 3 `rbtree` boundary packet
- no C-vs-Zig parity fixture for a Phase 3 `rbtree` boundary shape

## Non-Goals

This survey does not treat any of the following as the next honest Phase 3 step:

- porting the full balancing or mutation path from `lib/rbtree.c`
- widening `zigux/kernel/export_shim.zig` or `zigux/uapi/version.zig`
- counting the larger `chrdev_*` planning ladder as substitute closure for the roadmap-backed `rbtree` anchor

## Next Bounded Step

The next honest same-lane follow-on is one small Phase 3 `rbtree` boundary contract:

- one curated read-mostly ABI record
- one matching Zig binding shape
- one committed parity fixture that keeps the contract reviewable without widening into a full balancing port
