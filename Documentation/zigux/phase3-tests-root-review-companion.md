# Phase 3 Tests-Root Review Companion

This note keeps the tests-root view of the shared Phase 3 ABI packet explicit now that the shared `zigux_rbtree_root_view` lift is already landed.

## Status

- `PHASE3_TESTS_ROOT_PACKET=shared-abi-rbtree-lift-review-companion`
- `PHASE3_TESTS_ROOT_GUIDE=zigux/tests/README.md`
- `PHASE3_TESTS_ROOT_SURVEYS=Documentation/zigux/phase3-roadmap-gap-survey.md,Documentation/zigux/phase3-rbtree-interop-survey.md`
- `PHASE3_TESTS_ROOT_VALIDATOR=python3 scripts/zigux/check-phase3-tests-root-companion.py`
- `PHASE3_TESTS_ROOT_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/phase3_rbtree_shared_contract.zig,zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_TESTS_ROOT_SHARED_STATUS=landed-shared-zigux_rbtree_root_view-lift-explicit`
- `PHASE3_TESTS_ROOT_NEXT_STEP=keep-this-companion-aligned-with-validate-phase3-and-the-shared-abi-manifest-without-reopening-shared-abi-growth`

## Why this exists

The dedicated Phase 3 survey notes already explain that the shared `zigux_rbtree_root_view` lift is landed and that the remaining gap is review-facing alignment rather than missing shared code.

This companion keeps that same story easy to audit from the tests-root side:

- the shared ABI replay stays explicit through `zigux/tests/phase3_abi.zig` and `zigux/tests/phase3_abi_dump.zig`
- the dedicated shared-lift contract stays explicit through `zigux/tests/phase3_rbtree_shared_contract.zig`
- the manifest-backed packet stays explicit through `zigux/tests/fixtures/phase3_abi_manifest.json`
- the dedicated tests-root guard stays explicit through `python3 scripts/zigux/check-phase3-tests-root-companion.py`

## Bounded rule

Keep this companion aligned with `Documentation/zigux/phase3-roadmap-gap-survey.md`, `Documentation/zigux/phase3-rbtree-interop-survey.md`, and the shared Phase 3 ABI manifest packet.

Do not widen this note into fresh `chrdev_*` growth, new ABI records, or unrelated packet churn.
