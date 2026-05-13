# Phase 3 Kernel Export Shim Governance

This note closes the dedicated ownership and boundary-note gap for `zigux/kernel/export_shim.zig` inside the shared Phase 3 ABI packet.

## Scope

- `PHASE3_KERNEL_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_KERNEL_EXPORT_SHIM_PACKET=shared Phase 3 ABI substrate packet only`
- `PHASE3_KERNEL_EXPORT_SHIM_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_KERNEL_EXPORT_SHIM_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_KERNEL_EXPORT_SHIM_STARTER_SURVEY=Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `PHASE3_KERNEL_EXPORT_SHIM_HEADER_GOVERNANCE=Documentation/zigux/phase3-linux-zigux-header-governance.md`
- this note governs how the kernel-facing starter relay may grow without turning `zigux/kernel/` naming churn into fake Phase 3 progress

## Ownership

- canonical header layout, versioning, and export-status field ownership stays in `include/zigux/abi.h`
- accepted-header evaluation and boundary-header canonicalization ownership stays in `zigux/uapi/version.zig`
- starter `dev_t` companion ownership stays in `zigux/uapi/dev_t.zig` and `include/zigux/dev_t.h`
- Linux-facing aggregation ownership stays in `include/linux/zigux.h` plus `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `zigux/kernel/export_shim.zig` owns the kernel-facing relay layer that packages those canonical surfaces into explicit `ok()`, `errno()`, `normalize()`, `compatibilityStatus()`, `evaluateHeader()`, `extendsBoundary()`, and `requestedExtraBytes()` helpers for kernel-side callers
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md` still owns the starter export/UAPI route wording and shared replay reminders that sit beside this narrower kernel-facing relay

## Growth Rule

- `PHASE3_KERNEL_EXPORT_SHIM_GROWTH_RULE=new zigux/kernel starter relays may land only when the same bounded change also refreshes this note, the shared ABI slice, and the manifest-backed Phase 3 packet inventory.`
- keep `zigux/kernel/export_shim.zig` as a thin kernel-facing relay over already-owned ABI and UAPI surfaces rather than a second semantic home for header layout, enum ownership, or low-level helper policy
- new kernel-facing wrapper names without matching shared replay or manifest-backed evidence should be treated as churn, not Phase 3 closure
- repetitive suffix-chain relay growth inside `zigux/kernel/` does not count as product progress on its own

## Current State

- live `zigux/kernel/export_shim.zig` already reuses the shipped `Header`, `Compatibility`, `AcceptedHeader`, and `HeaderEvaluation` types from `zigux/uapi/version.zig`
- live `zigux/kernel/export_shim.zig` already keeps failure encoding reviewable through `ok()`, `errno()`, and `normalize()` instead of hiding export-status shaping in broader helper or header growth
- live `zigux/kernel/export_shim.zig` already exposes `compatibilityStatus()`, `evaluateHeader()`, `extendsBoundary()`, and `requestedExtraBytes()` so kernel-facing callers can stay on the shared boundary-header contract without inventing a second ABI home
- live `zigux/kernel/export_shim.zig` now also exposes status-tagged `encodeDeviceNumber()` and `lastDeviceNumberInRange()` relays over the shipped `zigux/uapi/dev_t.zig` starter companion without re-homing `dev_t` ownership into `zigux/kernel/`
- current `master` still ships no wider `zigux/kernel/` family beyond this starter relay, so the honest next step is governance and ownership clarity, not more kernel-surface proliferation

## Boundary

- this note does not move starter UAPI ownership out of `zigux/uapi/`
- this note does not move Linux-facing aggregation ownership out of `include/linux/zigux.h`
- this note does not authorize deeper kernel-port claims, driver shims, or low-level helper growth under `zigux/kernel/`
- if a future bounded change adds another kernel-facing substrate relay, refresh this note together with `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-abi-slice.md`, and `zigux/tests/fixtures/phase3_abi_manifest.json` in the same packet so the kernel-facing side of the boundary stays explicit

## Non-Goals

- this note does not claim new UAPI companions
- this note does not claim new bindings or header families
- this note does not claim runtime scheduler, workqueue, RCU, or driver-port progress
