# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that is directly readable on `master`.

## Present scripts-root packet

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Shared reminder contract

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` should keep the same narrowed packet visible from the docs root, checklist, tests root, and scripts root instead of rebuilding the older validator-first or installer-backed tranche.
- Keep the scripts-root reminder aligned with the live toolchain checker, the surviving kbuild and alignment guards, the kconfig bridge helper packet, the shipped closure-side validator entrypoint, and the required-make-route plus `zigux/Makefile` pair instead of reintroducing the missing closure-validator, installer, or direct cross-route packet as if it had already returned on `master`.
- Treat the adjacent bootstrap-note, shared-gap, and tests-root follow-up surfaces as separate same-lane review paths until they land, rather than folding those larger reminder packets back into this scripts-root sidecar.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the scripts-root Phase 2 reminder bounded to current-master truth while the remaining shared reminder surfaces land on their separate review paths.
