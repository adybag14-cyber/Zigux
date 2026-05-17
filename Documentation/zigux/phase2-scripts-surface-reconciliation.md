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

These are the current directly readable Phase 2 scripts-root anchors on `master`.

## Current repo-reality gaps

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/mk_elfconfig.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Outstanding scripts-root README drift

- `scripts/zigux/README.md` still presents `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate`, `make -C zigux phase2-cross`, and `make -C zigux phase2` routes as current Phase 2 scripts-root evidence even though fresh current-master reads still miss those branch-local, closure-side, cross-matrix, and make-route surfaces.
- Keep that README drift framed as the next bounded Lane 25 follow-up instead of folding it back into this note as if the scripts-root summary were already reconciled.

## Lane 25 boundary

Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth until the separate closure, cross-target, tool-restoration, and scripts-root README reconciliation lanes land.
