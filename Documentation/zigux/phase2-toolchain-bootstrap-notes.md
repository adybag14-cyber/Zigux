# Phase 2 Toolchain Bootstrap Notes

This note tracks the dedicated Phase 2 toolchain bootstrap companion on the active Lane 24 branch.

It stays branch-scoped: live `master` still lacks parts of the broader toolchain packet, but this lane branch now carries the shared validator, the manifest-packet checker, the dedicated Zig-version guard, the dedicated pin-scope helper, and Linux-style `zigux/Makefile` routes beside the surviving toolchain pinning guard, this bootstrap companion, the closure note, and the compact manifest.

## Status

- `PHASE2_TOOLCHAIN_BOOTSTRAP_STATUS=lane24-branch-restacked`
- `PHASE2_TOOLCHAIN_SURVIVING_GUARD=scripts/zigux/check-phase2-toolchain-pinning.py`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_GUARD=scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `PHASE2_TOOLCHAIN_ZIG_VERSION_GUARD=scripts/zigux/check-zig-toolchain.py`
- `PHASE2_TOOLCHAIN_WORKFLOW_SURFACE=.github/workflows/zigux-bootstrap.yml`
- `PHASE2_CLOSURE_COMPANION=Documentation/zigux/phase2-closure.md`
- `PHASE2_TOOL_MANIFEST=zigux/tests/fixtures/phase2_tool_manifest.json`
- `PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`
- `PHASE2_SHARED_VALIDATOR=scripts/zigux/validate-phase2.py`
- `PHASE2_SHARED_MAKEFILE=zigux/Makefile`

## Present Current Branch Packet

- dedicated bootstrap companion: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- surviving toolchain guard: `scripts/zigux/check-phase2-toolchain-pinning.py`
- dedicated toolchain pin-scope guard: `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- direct Zig-version guard: `scripts/zigux/check-zig-toolchain.py`
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
- current `master` now also carries `scripts/zigux/check-phase2-required-make-routes.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, so keep those master-only shared companions separate from the still-missing installer-backed helper when reading this toolchain note
- `scripts/zigux/check-phase2-toolchain-pin-scope.py` is now present on this lane branch as well as current `master`, so the remaining branch-side toolchain gap is the installer-backed helper rather than the direct pin-scope guard
- treat the installer-backed helper as the remaining current-master toolchain gap until that file is re-materialized on this branch too

## Review Notes

- `scripts/zigux/check-phase2-toolchain-pinning.py` remains the surviving direct toolchain guard on the branch; keep this note aligned with that checker while the dedicated pin-scope helper now travels with the same branch-local packet
- `scripts/zigux/check-zig-toolchain.py` is now directly readable on current `master`; keep this note aligned with that shared Zig-version guard while `scripts/zigux/install-zig.py` remains the missing installer-backed companion
- `scripts/zigux/check-phase2-toolchain-pin-scope.py` is now directly readable on the lane branch too, so keep this note explicit that the helper is part of the current branch-local toolchain evidence rather than a pending replay gap
- `scripts/zigux/check-phase2-tool-manifest-packets.py` keeps the branch-local manifest packet aligned with this note, the closure note, and the shared validators without implying that the installer-backed helper is already back on this branch
- the same manifest packet also keeps `scripts/zigux/check-phase2-required-make-routes.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` explicit as current-master-only shared companions instead of folding them into the same bucket as the still-missing installer helper
- `scripts/zigux/validate-phase2.py` and `zigux/Makefile` are now part of the branch-local shared toolchain packet, so this note should stop treating them as still-missing closure-side work
- `PHASE2_TOOLCHAIN_NEXT_STEP=restore the remaining installer-backed helper now that the shared validator, direct Zig-version guard, dedicated pin-scope helper, and Linux-style Makefile routes are back on the lane branch`
