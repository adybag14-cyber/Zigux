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
- `PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-and-shared-abi-root-view-lift-landed`
- `PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,include/zigux/rbtree.h,zigux/bindings/rbtree.zig,include/zigux/abi.h,zigux/bindings/abi.zig,zigux/helpers/rbtree_view.zig,zigux/helpers/rbtree_root_view.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase3-rbtree-slice.md,Documentation/zigux/phase3-rbtree-interop-survey.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_root_view_survey.zig,zigux/tests/phase3_rbtree_manifest.json,zigux/tests/phase3_rbtree_shared_contract.zig,zigux/tests/phase3_rbtree_dump.zig,zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c,zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json`
- `PHASE3_CURRENT_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig`
- `PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-packet-now-carries-rbtree-root-view-through-curated-shared-header-and-binding`
- `PHASE3_CURRENT_RBTREE_SHARED_CATALOG=phase3-abi-manifest-catalogs-dedicated-rbtree-boundary-shared-replay-and-the-still-open-survey-wording-gap`
- `PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors`
- `PHASE3_INTEROP_GAP=survey-and-validator-wording-still-lag-the-landed-shared-rbtree-lift-while-chrdev-tail-growth-keeps-expanding`
- `PHASE3_NEXT_BOUNDED_STEP=align-shared-phase3-survey-and-validator-wording-before-more-chrdev-growth`
- `PHASE3_VALIDATION_ROUTE=scripts/zigux/validate-phase3.py,make -C zigux phase3-validate,.github/workflows/zigux-bootstrap.yml`

## Current Gap

The largest roadmap-backed interop gap is no longer the total absence of a Phase 3 `rbtree` helper or boundary packet, and it is no longer the absence of the first shared Phase 3 `rbtree` root-view lift either.

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
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`

The remaining honest gap is narrower and more review-facing:

- the roadmap wording and some survey-owned wording still lag the landed shared `rbtree` lift in `include/zigux/abi.h` and `zigux/bindings/abi.zig`
- the live Phase 3 build graph still carries deeper `chrdev_*` tail packets well beyond the original four roadmap anchors, which makes honest survey and validator wording more important than still more shared-ABI growth right now
- the next safe same-family move is therefore to finish aligning the shared survey and validator packet with the landed shared `rbtree` replay rather than pretending the shared lift is still missing or treating extra `chrdev_*` growth as roadmap closure

That is a better state than before, because the repo now has both a real dedicated Phase 3 `rbtree` boundary packet and a landed shared root-view lift inside the canonical ABI packet. The shared ABI replay already covers `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`, and that replay now runs through the curated shared `include/zigux/abi.h` plus `zigux/bindings/abi.zig` surface instead of depending only on the dedicated `rbtree` header and binding. The shared ABI manifest already catalogs that shared replay alongside the dedicated packet and the review guards, so the remaining Phase 3 gap is not missing shared code. It is the smaller survey and validator wording drift around already-landed shared ABI reality.

## Validation Route

The dedicated roadmap-gap survey is still meant to be reviewed through the shared validator-first path rather than as a standalone bootstrap or release entrypoint.

- `python3 scripts/zigux/validate-phase3.py`
- `make -C zigux phase3-validate`
- the bootstrap workflow replays the same shared validator route before the broader Phase 3 ABI and interop tests run
- `python3 scripts/zigux/check-phase3-canonical-survey-manifest.py` stays inside that same validator-first route so the canonical survey-script list in `validate-phase3.py` and the committed `zigux/tests/fixtures/phase3_abi_manifest.json` packet cannot drift apart silently
- `python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py`, `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py`, `python3 scripts/zigux/check-phase3-rbtree-shared-lift-contract.py`, `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`, `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `python3 scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`, `python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py`, `python3 scripts/zigux/check-phase3-abi-layout-packet.py`, `python3 scripts/zigux/check-phase3-abi-binding-constants.py`, `python3 scripts/zigux/check-phase3-tooling-packet.py`, `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py`, `python3 scripts/zigux/check-phase3-validation-flow.py`, `python3 scripts/zigux/check-phase3-build-roots.py`, and `python3 scripts/zigux/check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that same validator-first route instead of standalone release paths
- `python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` should now be treated as the next bounded follow-on surface for wording alignment around the already-landed shared lift rather than as proof that the shared lift itself is still missing

## Next Bounded Step

The next honest Phase 3 move in this survey family is not another new shared `rbtree` record.

It is one bounded survey-and-validator alignment pass before more char-device expansion:

- align the remaining shared Phase 3 survey wording with the landed shared `zigux_rbtree_root_view` lift in `include/zigux/abi.h` and `zigux/bindings/abi.zig`
- keep the shared ABI replay, manifest catalog, and dedicated `rbtree` packet explicit in that wording
- stop there; do not widen this lane into more `chrdev_*` tail growth or unrelated Phase 3 packet churn