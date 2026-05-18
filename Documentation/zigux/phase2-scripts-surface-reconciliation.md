# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that Lane 25 keeps aligned on `master`.

## Directly readable scripts-root anchors

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
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Remaining repo-reality gaps

- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

Treat those paths as the remaining repo-reality gaps on current `master`, not as shipped Phase 2 scripts-root evidence.

## Current aligned packet

- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, and `zigux/Makefile` now all keep `scripts/zigux/validate-phase2-closure.py` inside the present Phase 2 packet instead of classifying it as missing.
- The live reminder surfaces keep only `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` in repo-reality-gap wording.
- Keep this scripts-surface sidecar focused on fail-closing that aligned scripts-root packet while the broader artifact-diff note and the other Lane 25 sidecars keep their separate surfaces.
- Do not treat the remaining installer or direct cross-route companions as returned until current `master` materializes them.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, manifest, closure-side, and make-wrapper packet aligned around the restored closure validator without reopening the broader shared docs or artifact-diff surfaces.
