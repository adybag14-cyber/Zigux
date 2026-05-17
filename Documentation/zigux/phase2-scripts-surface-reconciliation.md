# Phase 2 Scripts Surface Reconciliation

This note records the current scripts-root Phase 2 packet that is directly readable on `master`.

## Present scripts-root packet

- `scripts/zigux/README.md`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`

These are the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/mk_elfconfig.zig`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Shared reminder contract

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should match the same present-versus-gap inventory tracked here, including `scripts/zigux/kconfig/confdata_bridge.zig` as a present anchor and the still-missing closure-side, cross-matrix, toolchain-helper, genksyms, and make-route surfaces as repo-reality gaps.
- Keep the scripts-root reminder aligned with the live kconfig bridge packet and the surviving alignment guards instead of reintroducing the older closure-side validator stack before those direct paths return on `master`.
- `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` still need that same narrowing pass before Lane 25 is fully closed, so treat those two shared reminder surfaces as remaining same-lane drift instead of proof that the older closure-side, cross-matrix, or make-route packet has returned on `master`.

## Lane 25 boundary

Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth, including the still-pending docs-root and review-checklist narrowing pass, until the separate closure, cross-target, and tool-restoration lanes land.
