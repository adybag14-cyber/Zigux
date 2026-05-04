# Phase 3 Roadmap Gap Survey

This note records the current Phase 3 ABI and interop gap between the roadmap contract and the live Zigux tree.

## Status

- `PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c`
- `PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig`
- `PHASE3_CURRENT_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header`
- `PHASE3_CURRENT_UAPI=zigux/uapi/version.zig`
- `PHASE3_CURRENT_UAPI_SCOPE=version-and-boundary-header`
- `PHASE3_UAPI_BOUNDARY_GAP=version-and-boundary-header-surface-is-still-below-full-uapi-shim-destination`
- `PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig`
- `PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig`
- `PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-exists-shared-abi-lift-still-missing`
- `PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,include/zigux/rbtree.h,zigux/bindings/rbtree.zig,zigux/helpers/rbtree_view.zig,zigux/helpers/rbtree_root_view.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase3-rbtree-slice.md,Documentation/zigux/phase3-rbtree-interop-survey.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_root_view_survey.zig,zigux/tests/phase3_rbtree_manifest.json,zigux/tests/phase3_rbtree_shared_contract.zig,zigux/tests/phase3_rbtree_dump.zig,zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json`
- `PHASE3_CURRENT_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig`
- `PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-replay-already-reuses-dedicated-rbtree-layout-shared-header-lift-still-missing`
- `PHASE3_CURRENT_RBTREE_SHARED_CATALOG=phase3-abi-manifest-catalogs-shared-rbtree-replay-and-lift-guards`
- `PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors`
- `PHASE3_INTEROP_GAP=shared-phase3-abi-rbtree-lift-still-missing`
- `PHASE3_NEXT_BOUNDED_STEP=shared-abi-rbtree-root-view-before-more-chrdev-growth`
- `PHASE3_VALIDATION_ROUTE=scripts/zigux/validate-phase3.py,make -C zigux phase3-validate,.github/workflows/zigux-bootstrap.yml`

## Current Gap

The largest roadmap-backed interop gap is no longer the total absence of a Phase 3 `rbtree` helper or boundary packet.

That packet now exists through:

- `zigux/helpers/rbtree_view.zig`
- `zigux/helpers/rbtree_root_view.zig`
- `include/zigux/rbtree.h`
- `zigux/bindings/rbtree.zig`
- `zigux/tests/phase3_rbtree_dump.zig`
- `zigux/tests/fixtures/phase3_rbtree/expected.json`
- `zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c`
- `Documentation/zigux/phase3-rbtree-slice.md`
- `Documentation/zigux/phase3-rbtree-interop-survey.md`
- `zigux/tests/phase3_rbtree_survey.zig`
- `zigux/tests/phase3_rbtree_root_view_survey.zig`
- `zigux/tests/phase3_rbtree_manifest.json`
- `zigux/tests/phase3_rbtree_shared_contract.zig`
- `scripts/zigux/check-phase3-rbtree-shared-lift-contract.py`

The remaining honest gap is narrower:

- there is still no curated `rbtree` record in `include/zigux/abi.h`
- there is still no matching shared `zigux/bindings/abi.zig` layout type for a Phase 3 `rbtree` boundary packet
- the shared `phase3_abi` replay still reaches `rbtree` through `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig` rather than through a curated shared `abi.h` plus `abi.zig` record

That is a better state than before, because the repo now has a real dedicated Phase 3 `rbtree` boundary packet, and the shared ABI replay already covers `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`. `zigux/helpers/rbtree_root_view.zig`, `zigux/tests/phase3_rbtree_root_view_survey.zig`, `zigux/tests/phase3_rbtree_shared_contract.zig`, and `scripts/zigux/check-phase3-rbtree-shared-lift-contract.py` now also keep the reusable root-view helper plus the planned shared-lift contract explicit before the canonical shared header and binding grow. The shared ABI manifest now also catalogs that shared replay and its lift guards, so the Phase 3 gap is no longer tangled up with inventory drift. The low-level wrapper packet has also moved forward around the same substrate: `zigux/tests/phase3_low_level_wrappers.zig` now keeps the focused atomic, barrier, scoped MMIO, width-specific policy MMIO, and generic decoded-policy `readScopedWithPolicy()` or `writeScopedWithPolicy()` bridge replay explicit instead of leaving that routed MMIO helper surface visible only through the broader policy-and-unsafe packet. When the shared `rbtree` lift lands, it should reuse the dedicated `zigux_rbtree_root_view` layout and `root_flag_empty`, `root_flag_cached`, and `root_flag_leftmost_valid` constants unchanged inside the shared packet.

## Validation Route

The dedicated roadmap-gap survey is reviewed through the shared validator-first path rather than as a standalone bootstrap or release entrypoint.

- `python3 scripts/zigux/validate-phase3.py`
- `make -C zigux phase3-validate`
- the bootstrap workflow replays the same shared validator route before the broader Phase 3 ABI and interop tests run
- `python3 scripts/zigux/check-phase3-canonical-survey-manifest.py` stays inside that same validator-first route so the canonical survey-script list in `validate-phase3.py` and the committed `zigux/tests/fixtures/phase3_abi_manifest.json` packet cannot drift apart silently
- `python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py`, `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py`, `python3 scripts/zigux/check-phase3-rbtree-shared-lift-contract.py`, `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`, `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `python3 scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`, `python3 scripts/zigux/check-phase3-abi-layout-packet.py`, `python3 scripts/zigux/check-phase3-abi-binding-constants.py`, `python3 scripts/zigux/check-phase3-tooling-packet.py`, `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py`, `python3 scripts/zigux/check-phase3-validation-flow.py`, `python3 scripts/zigux/check-phase3-build-roots.py`, and `python3 scripts/zigux/check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that same validator-first route instead of standalone release paths
- `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` also stays inside that same validator-first route so the dedicated `rbtree` survey, shared-lift contract, and remaining shared-ABI gap stay reviewable without becoming a standalone release path

## Next Bounded Step

The next honest Phase 3 move is one small curated `rbtree` root view in the shared ABI packet before more char-device expansion:

- one shared header-and-binding shape
- one shared ABI replay path that no longer depends on the dedicated `rbtree` include path
- one validator-backed note refresh
- reuse the dedicated `zigux_rbtree_root_view` layout and flag constants unchanged