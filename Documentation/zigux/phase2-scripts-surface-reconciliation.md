# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root packet that is directly readable on `master`.

## Present scripts-root packet

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/tests/fixtures/phase2_tool_manifest.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/mk_elfconfig.zig`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Shared reminder contract

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` still need the same narrowing pass to match this present-versus-gap inventory, including `scripts/zigux/check-zig-toolchain.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` as present anchors.
- `scripts/zigux/README.md` is already narrowed to the current direct packet on this branch and should stay aligned with `Documentation/zigux/phase2-scripts-surface-reconciliation.md` while the broader shared docs-root and tests-root reminder surfaces catch up.
- `Documentation/zigux/phase2-shared-reminder-gap.md` should stay explicit while `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` still encode the broader pre-narrowing Phase 2 packet.
- Keep the scripts-root reminder aligned with the live toolchain checker, the live kconfig bridge packet, and the surviving alignment guards instead of reintroducing the older closure-side validator stack before those direct paths return on `master`.

## Lane 25 boundary

Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth until the remaining shared docs-root, review-checklist, tests-root, and checker surfaces are narrowed and the separate closure, cross-target, and tool-restoration lanes land.
