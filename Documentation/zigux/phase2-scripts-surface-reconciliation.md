# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that Lane 25 keeps aligned on `master`.

## Directly readable scripts-root anchors

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current aligned packet

- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/Makefile` now all keep `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `scripts/zigux/validate-phase2-closure.py` inside the current packet instead of framing any of them as repo-reality gaps.
- The live reminder packet now stays aligned across the shipped toolchain checker, installer helper, direct cross-route checker, kconfig bridge helpers, closure-side validator pair, shipped make-wrapper routes, and fixture roster already visible on current `master`.
- Keep this scripts-surface sidecar focused on fail-closing that returned scripts-root packet while the shared docs, bootstrap-note, manifest-root, and artifact-diff lane packets keep their separate surfaces.

## Current repo-reality gaps

- No current repo-reality gaps remain inside the bounded scripts-root toolchain, installer, direct cross-route, closure-side, make-wrapper, and fixture packet on current `master`.
- Treat future drift here as a reminder-surface mismatch first, not as evidence that the returned installer or direct cross-route packet disappeared.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the present scripts-root, bootstrap-note, tests-root, manifest, closure-side, and make-wrapper packet aligned around the returned installer, direct cross-route, and closure-validator surfaces without reopening the broader shared docs or artifact-diff sidecars.
