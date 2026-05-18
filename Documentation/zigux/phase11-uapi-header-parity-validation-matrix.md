# Phase 11 UAPI Header Parity Validation Matrix

This document records the bounded current-head validation matrix for the Phase 11 shared header-boundary packet.

## Status

- `PHASE11_UAPI_HEADER_MATRIX_STATUS=adjacent_proof_shard_readback_only`
- lane: `P11-L02`
- reviewed against live `master`
- scope: keep the shared header-boundary reminder packet truthful using directly readable proof and note surfaces without reviving missing shared replay, manifest, or checker paths and without widening into tty-core or watchdog-core ownership
- current direct-readback packet:
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `drivers/tty/hvc/hvc_console.h`
- current direct contents reads in this lane do not rematerialize:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`

## Roadmap Anchor

- Phase 11 still treats straightforward watchdog and HVC surfaces as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.
- This matrix stays useful only if it reflects the smaller current-head packet that is directly readable today.

## Why This Exists

The lane-owned header-boundary matrix still matters, but current `master` no longer supports the older claim that the whole shared UAPI-header replay packet is directly readable and machine-checked through a returned survey source, manifest, checker, and shared build route.

What current `master` does still expose is a narrower adjacent packet: the matrix note, the older survey note, the shared sequencing notes that keep this packet separate from the driver-local HVC and watchdog lanes, the HVC matrix that now records `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, and `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` as directly readable proof shards, the surviving HVC-focused build inventory, and the exported `drivers/tty/hvc/hvc_console.h` header surface.

This matrix therefore records current-head truthfulness for that smaller adjacent packet instead of replaying the older shared-packet wording as if all of its direct anchors had returned.

## Current-Head Matrix

| lane surface | current evidence | bounded gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| exported-header proof shard | `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, and `drivers/tty/hvc/hvc_console.h` keep the bounded HVC exported-header shard directly readable through `winsize` layout, `struct hv_ops` callback-table layout, and exported helper signature proof | the focused proof build in `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` together with direct readback of the export-surface proof keeps the surviving public-header shard reviewable | if `hvc_console.h` grows or reorders the exported helper surface, `winsize`, or the callback table, refresh both proof shards and this matrix together in one bounded pass | notifier callback semantics, host-backed hypervisor transport, live tty registration, or broader HVC runtime behavior |
| shared reminder posture | `Documentation/zigux/phase11-driver-lane-sequencing.md` and `Documentation/zigux/phase11-validation-matrix-gap-survey.md` keep this matrix adjacent shared evidence rather than a driver-local HVC or watchdog lane member | direct reread of this matrix together with the sequencing and matrix-gap notes keeps the lane split honest | refresh `Documentation/zigux/phase11-uapi-header-parity-survey.md` so it matches the smaller surviving proof-shard packet instead of the older shared replay wording | folding this packet into `P11-L16`, the watchdog-local lanes, or broad contributor-note ownership |
| older shared replay family | `Documentation/zigux/phase11-uapi-header-parity-survey.md` still records the older shared packet vocabulary, but current direct contents reads do not rematerialize `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/tests/phase11_build.zig`, `Documentation/zigux/phase11-shared-replay-contract.md`, or `scripts/zigux/check-phase11-header-boundary-packet.py` | keep those paths framed as repo-reality gaps or archival wording until a future reread proves they returned | if any one of those shared packet anchors rematerializes, refresh this matrix in the same pass that restores the corresponding survey wording | claiming shared replay, manifest, checker, or build-route coverage as current-head evidence from historical wording alone |
| build inventory boundary | `zigux/tests/fixtures/phase11_build_inventory.json` is directly readable again, but its current body records the narrower HVC continuity packet rather than a returned header-boundary replay roster | direct reread of the inventory file is enough to keep this boundary explicit | add header-boundary inventory wording only when a directly readable shared replay file returns and needs to be tracked explicitly | using the HVC-only inventory as proof that the full shared header-boundary packet is landed again |

## Review Rules

- Treat this matrix as current-head truthfulness for an adjacent shared header-boundary packet, not as proof that the older shared replay family is back on `master`.
- Do not use the returned exported-header proof shards to overclaim shared watchdog proof, a restored shared build route, checker coverage, notifier execution, tty registration, watchdog-core integration, or whole-Phase-11 closure.
- Keep `Documentation/zigux/phase11-uapi-header-parity-survey.md` explicit as a readable note whose broader packet claims now need a same-lane refresh rather than as direct proof that the missing survey source, manifest, checker, and shared replay route have already returned.
- If a future reread restores one or more of the missing shared packet anchors, update this matrix together with the survey note in the same bounded pass so the header-boundary packet stays reviewable without drift.
