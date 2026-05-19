# Phase 3 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the current Phase 3 ABI and interop packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_RELEASE_CLOSED=no`
- shared-summary lane owner: `pmo-release`
- scope: keep the bounded Phase 3 ABI, export/UAPI, header-family, policy, and low-level-wrapper packet reviewable on current `master` without implying wider header-family binding closure or later runtime and driver delivery
- shared slice companion: `Documentation/zigux/phase3-abi-slice.md`
- header-family survey companion: `Documentation/zigux/phase3-abi-header-family-survey.md`
- export/UAPI survey companion: `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- policy companion: `Documentation/zigux/phase3-policy-slice.md`
- low-level-wrapper companion: `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- linux-header governance companion: `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- shared validator bundle: `scripts/zigux/validate-phase3.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- catalog guard bundle: `scripts/zigux/phase3_catalog.py` and `scripts/zigux/check-phase3-catalog-selftest.py`
- shared manifest companion: `zigux/tests/fixtures/phase3_abi_manifest.json`

## Repo-Reality Correction

Current `master` now directly serves both `Documentation/zigux/phase3-abi-header-family-survey.md` and `scripts/zigux/validate-phase3-abi-header-family-survey.py`.

Keep release coordination aligned to those directly readable current-master files rather than repeating older wording that treated the header-family survey pair as missing.

The remaining wider Phase 3 gap in that family is still the separate broader header-family binding follow-through, including `zigux/bindings/header_family.zig`, not the survey pair itself.

## Owner Split

- PMO / Release Management: keep this matrix, `Documentation/zigux/phase3-abi-slice.md`, the header-family survey, the export/UAPI survey, the policy note, the low-level-wrapper survey, and the shared validator bundle aligned around the same active-not-closed release posture
- shared ABI packet: keep `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump_current.zig`, `zigux/tests/build.zig`, and `zigux/tests/fixtures/phase3_abi_manifest.json` explicit as the current shared ABI proof packet
- export/UAPI and header-family packet: keep `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/bindings/dev_t.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` explicit as the current bounded relay and layout packet
- policy and low-level-wrapper packet: keep `Documentation/zigux/phase3-policy-slice.md`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` explicit as adjacent release-surface support without promoting them into full tranche closure by themselves

## Shared Release Order

1. `python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test`
2. `python3 scripts/zigux/validate-phase3.py`
3. `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test`
4. `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
5. `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
6. `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test`
7. `zig build phase3-abi-core-packet --build-file zigux/tests/build.zig`
8. `zig build phase3-dump --build-file zigux/tests/build.zig`
9. `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
10. `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

Keep this validator-first then replay-second order explicit in release wording. Do not skip straight to the focused replay routes when the shared Phase 3 docs or manifest have drifted.

## Release Blocker

The current Phase 3 packet is reviewable and partially replayable, but it is not ready for tranche closure.

Keep the broader header-family binding follow-through framed as the blocking shared-family gap:

- `zigux/bindings/header_family.zig`

Do not let release wording treat the now-present survey pair as a closure blocker that still needs to be recreated, and do not let the remaining binding gap be hidden behind the newer survey note.

## Boundaries

- This matrix does not close Phase 3.
- This matrix does not imply that the broader header-family binding lane has landed.
- This matrix does not widen Phase 3 into Phase 4 rollback ownership, Phase 9 runtime pilots, or later driver phases.
- `Documentation/zigux/freeze-map.md` remains the owner for deeper study-only and freeze-in-C boundaries outside this bounded ABI packet.

## Next Bounded Step

Leave this matrix parked unless a fresh repo-first reread finds drift between:

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/check-phase3-catalog-selftest.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`

If the next Phase 3 PMO follow-through is needed after that, prefer one narrow truthfulness repair in the shared docs-root packet or one explicit binding-gap note rather than widening into helper-local implementation work.
