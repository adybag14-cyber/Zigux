# Phase 2 Scripts Surface Reconciliation

This note records the current scripts-root Phase 2 packet that is directly readable on `master`.

## Present scripts-root packet

- `scripts/zigux/README.md`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
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
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`

Treat those paths as active repo-reality gaps on current `master`, not as shipped scripts-root evidence.

## Lane 25 boundary

Lane 25 should use this note to keep Phase 2 reminder work bounded to current-master truth until the separate closure and tool-restoration lanes land.
