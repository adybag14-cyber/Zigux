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
- `PHASE3_RBTREE_PHASE3_BOUNDARY_STATUS=dedicated-boundary-and-shared-abi-root-view-lift-landed`
- `PHASE3_RBTREE_NON_GOALS=no-balancing-port,no-export-shim-growth,no-uapi-growth`
- `PHASE3_RBTREE_NEXT_BOUNDED_STEP=align-phase3-docs-root-summary-with-landed-shared-rbtree-lift`
- `PHASE3_RBTREE_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json`
- `PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet`
- `PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid`
- `PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root`
- `PHASE3_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig`
- `PHASE3_RBTREE_SHARED_PACKET_CATALOG=phase3_abi_manifest-catalogs-dedicated-rbtree-boundary-shared-replay-and-shared-lift-guards`
- `PHASE3_RBTREE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py`
- `PHASE3_RBTREE_SHARED_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_RBTREE_SHARED_MAKE_GATE=make -C zigux phase3-validate`

## Roadmap Anchor

Phase 3 names `lib/rbtree.c` as one of the four permanent C/Zigux boundary anchors. The current bounded task is no longer to prove that a dedicated boundary exists. The current bounded task is to keep the landed shared root-view lift and the surrounding survey packet reviewable.

## Current Evidence

The repo already carries real `rbtree` evidence in two adjacent packets:

- `tools/lib/rbtree.zig` plus `Documentation/zigux/phase1-closure.md` record the earlier host-helper parity lane
- `lib/rbtree.zig`, `Documentation/zigux/phase7-rbtree-slice.md`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` record the later runtime-helper lane

This Phase 3 lane now carries both the helper-local packet and the full dedicated-plus-shared boundary packet:

- `zigux/helpers/rbtree_view.zig` provides a bounded read-mostly summary over the existing runtime `rbtree` surface
- `zigux/helpers/rbtree_root_view.zig` keeps the dedicated root-view constructor and canonicalization path explicit for the shared replay too
- `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig` keep the dedicated `rbtree` root view reviewable on its own
- `zigux/tests/phase3_rbtree_dump.zig` plus `zigux/tests/fixtures/phase3_rbtree/expected.json` and `zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c` keep that dedicated boundary replayable across C and Zig
- `include/zigux/abi.h` and `zigux/bindings/abi.zig` now also carry the shared `zigux_rbtree_root_view` lift inside the canonical Phase 3 ABI packet
- `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json` keep the shared ABI replay explicit, including the canonical empty-root, cached-leftmost-root, and uncached-root samples
- `zigux/tests/phase3_rbtree_shared_contract.zig` and `scripts/zigux/check-phase3-rbtree-shared-lift-contract.py` now keep the dedicated layout, shared lift, and sample-record packet aligned before the broader ABI lane moves again
- the shared Phase 3 ABI manifest now explicitly catalogs the dedicated `rbtree` packet, the shared replay files, and the shared-lift guards, so this packet is no longer missing inventory or shared-code evidence

The remaining same-family gap is therefore review-facing rather than implementation-facing: the docs-root Phase 3 summary and any still-coupled survey wording need to stay aligned with this already-landed shared `rbtree` lift.

## Validation Path

The live Phase 3 validation packet now exposes this survey through dedicated and shared gates:

- `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` keeps this dedicated survey note, the broader `Documentation/zigux/phase3-roadmap-gap-survey.md` note, the helper slice note, and the repo-backed evidence paths aligned
- `python3 scripts/zigux/check-phase3-rbtree-shared-lift-contract.py` keeps the dedicated root-view layout, shared ABI lift, sample records, and manifest-backed packet explicit under one focused contract check
- `python3 scripts/zigux/validate-phase3.py --slug abi` keeps that shared-lift contract inside the broader Phase 3 ABI validation path instead of leaving it as prose-only context
- `make -C zigux phase3-validate` remains the shared wrapper entrypoint for the broader bounded ABI packet, so this survey stays reviewable through the same published Phase 3 gate

## Remaining Gap

Current `master` no longer lacks the shared `rbtree` root-view lift itself.

Current `master` still needs the surrounding docs-root summary and survey wording to stay synchronized with that landed lift:

- keep the dedicated and shared replay paths explicit in the survey packet
- keep the shared ABI manifest catalog and shared-lift contract checker in the same bounded review packet
- avoid treating further `chrdev_*` tail growth as a substitute for roadmap-backed `rbtree` review discipline

## Non-Goals

This survey does not treat any of the following as the next honest Phase 3 step:

- porting the full balancing or mutation path from `lib/rbtree.c`
- widening `zigux/kernel/export_shim.zig` or `zigux/uapi/version.zig`
- counting the larger `chrdev_*` planning ladder as substitute closure for the roadmap-backed `rbtree` anchor

## Next Bounded Step

The next honest same-lane follow-on is one bounded docs-root and survey-summary alignment pass:

- align the docs-root Phase 3 summary with the landed `zigux_rbtree_root_view` lift and keep any still-coupled survey wording in sync
- keep the dedicated packet, shared replay, and shared-lift contract explicit in that wording
- stop there; do not widen this lane into more `chrdev_*` tail growth or unrelated Phase 3 packet churn
