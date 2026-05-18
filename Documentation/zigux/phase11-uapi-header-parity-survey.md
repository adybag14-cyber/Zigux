# Phase 11 UAPI Header Parity Survey
## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=adjacent_proof_shard_readback_only`
- lane: `P11-L18`
- reviewed against live `master`
- scope: keep the shared header-boundary reminder packet truthful using directly readable proof and note surfaces without reviving missing shared replay, manifest, or checker paths and without widening into tty-core or watchdog-core ownership

## Current Repo Reality
- directly readable current-head packet:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `drivers/tty/hvc/hvc_console.h`
- current direct contents reads do not rematerialize:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`

## Roadmap Fit
- Phase 11 still treats bounded watchdog and HVC surfaces as the simple-production-driver anchors.
- Phase 11 still requires reviewable validation, matrix evidence, and failure-mode discipline before expansion.
- This survey stays useful only if it reflects the smaller current-head packet that is directly readable today rather than replaying older shared-route wording as if it were still landed.

## Current-Head Boundary
- `phase11-hvc-export-surface-proof`: `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, and `drivers/tty/hvc/hvc_console.h` keep the surviving exported HVC header shard directly readable on current `master`, including the bounded `winsize` layout, the `struct hv_ops` callback table, and the exported helper signature surface.
- `phase11-build-inventory-boundary`: `zigux/tests/fixtures/phase11_build_inventory.json` is directly readable again, but its current body records the narrower HVC continuity packet rather than a returned header-boundary replay roster.
- `phase11-top-level-route-gap`: `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` do not currently advertise a Phase 11 header-boundary replay route, so this survey must not imply that a shared make or workflow gate is already restored.
- `phase11-shared-replay-gap`: until `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/tests/phase11_build.zig`, `Documentation/zigux/phase11-shared-replay-contract.md`, and `scripts/zigux/check-phase11-header-boundary-packet.py` rematerialize in direct readback, keep the older shared replay family framed as a repo-reality gap rather than current-head evidence.

## Shared Versus Dedicated Replay
- directly readable proof-shard sources: `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` and `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- directly readable proof-shard replay: `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig --summary all`
- broader top-level Phase 11 routes currently stop short of a shared header-boundary replay on current `master`
- `zigux/tests/fixtures/phase11_build_inventory.json` should be read as HVC continuity evidence only while its `build_test_names`, module roots, and replay markers remain HVC-only.
- if a future reread restores any of the missing shared packet anchors, refresh this survey in the same bounded pass that restores those anchors so the public header-boundary packet becomes reviewable again without stale carryover wording.

## Why This Stays Bounded

- The current packet proves only the smaller directly readable header-boundary evidence and the gap between that evidence and the older shared replay wording.
- It does not claim returned `watchdog_info` or `winsize` layout proofs outside the surviving HVC exported-header shard, a restored shared build route, restored checker coverage, tty registration parity, notifier execution, watchdog-core integration, or whole-Phase-11 closure.
- Any future packet rematerialization or driver-local handoff still belongs in the smallest same-family follow-up that restores the missing direct-read anchors before widening into broader driver or contributor-note ownership.
