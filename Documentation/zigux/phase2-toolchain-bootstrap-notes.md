# Phase 2 Toolchain Bootstrap Notes

This note tracks the dedicated Phase 2 toolchain bootstrap companion on the active Lane 24 branch.

It stays branch-scoped: live `master` still lacks parts of the broader toolchain packet, but this lane branch now carries the shared validator, the manifest-packet checker, the dedicated toolchain pin-scope checker, and Linux-style `zigux/Makefile` routes beside the surviving toolchain pinning guard, this bootstrap companion, the closure note, and the compact manifest.

## Status

- `PHASE2_TOOLCHAIN_BOOTSTRAP_STATUS=lane24-branch-widened`
- `PHASE2_TOOLCHAIN_SURVIVING_GUARD=scripts/zigux/check-phase2-toolchain-pinning.py`
- `PHASE2_TOOLCHAIN_WORKFLOW_SURFACE=.github/workflows/zigux-bootstrap.yml`
- `PHASE2_CLOSURE_COMPANION=Documentation/zigux/phase2-closure.md`
- `PHASE2_TOOL_MANIFEST=zigux/tests/fixtures/phase2_tool_manifest.json`
- `PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`
- `PHASE2_SHARED_VALIDATOR=scripts/zigux/validate-phase2.py`
- `PHASE2_SHARED_MAKEFILE=zigux/Makefile`

## Present Current Branch Packet

- dedicated bootstrap companion: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- surviving toolchain guard: `scripts/zigux/check-phase2-toolchain-pinning.py`
- dedicated toolchain pin-scope checker: `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- shared Phase 2 validator: `scripts/zigux/validate-phase2.py`
- manifest-packet checker: `scripts/zigux/check-phase2-tool-manifest-packets.py`
- bounded Linux-style route surface: `zigux/Makefile`
- current bootstrap workflow surface: `.github/workflows/zigux-bootstrap.yml`
- shared reminder companions:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
- closure packet companions:
  - `Documentation/zigux/phase2-closure.md`
  - `scripts/zigux/validate-phase2-closure.py`
  - `zigux/tests/fixtures/phase2_tool_manifest.json`
  - `scripts/zigux/check-phase2-tool-manifest-packets.py`

## Current Gaps

- repeated authenticated current-branch reads still returned missing for:
  - `scripts/zigux/install-zig.py`
  - `scripts/zigux/check-zig-toolchain.py`
- treat the remaining installer-backed and dedicated Zig-version helper packet as the remaining toolchain-side Phase 2 gaps on this branch until those files are re-materialized here too

## Review Notes

- `scripts/zigux/check-phase2-toolchain-pinning.py` remains the surviving direct toolchain guard on the branch, and `scripts/zigux/check-phase2-toolchain-pin-scope.py` now keeps the dedicated pin-scope companion explicit on the same branch-local packet
- `scripts/zigux/check-phase2-tool-manifest-packets.py` keeps the branch-local manifest packet aligned with this note, the closure note, and the shared validators without implying that the remaining dedicated Zig-version helpers are already back
- `scripts/zigux/validate-phase2.py` and `zigux/Makefile` are now part of the branch-local shared toolchain packet, so this note should stop treating them as still-missing closure-side work
- `PHASE2_TOOLCHAIN_NEXT_STEP=restore one remaining Zig-version helper at a time now that the dedicated pin-scope checker, the shared validator, and Linux-style Makefile routes are back on the lane branch`
