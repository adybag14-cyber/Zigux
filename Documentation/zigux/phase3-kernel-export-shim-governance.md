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
- `zigux/kernel/export_shim.zig` owns the kernel-facing relay layer that packages those canonical surfaces into explicit `Header`, `HeaderCompatibility`, `HeaderAcceptance`, `HeaderEvaluation`, `CompatibilityDecision`, `DeviceEncodingResult`, and `DeviceNumber` result shapes for kernel-side callers
- `zigux/kernel/export_shim.zig` also owns the thin kernel-side relay families that keep constructor, predicate, compatibility, explicit status shaping, and starter decode helpers reviewable through `versionedHeader()`, `canonicalHeader()`, `boundaryHeader()`, `compatibleHeader()`, `header()`, `isCurrentAbiVersion()`, `isCompatibleSize()`, `isCanonicalSize()`, `headerCompatibility()`, `acceptHeader()`, `evaluateHeader()`, `compatibilityStatus()`, `isCompatibleHeader()`, `isCanonicalHeader()`, `canonicalizeHeader()`, `extendsBoundary()`, `requestedExtraBytes()`, `ok()`, `errno()`, `normalize()`, `isOk()`, `encodeDeviceNumber()`, `lastDeviceNumberInRange()`, and `decodeDeviceNumber()`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md` still owns the starter export/UAPI route wording and shared replay reminders that sit beside this narrower kernel-facing relay

## Growth Rule

- `PHASE3_KERNEL_EXPORT_SHIM_GROWTH_RULE=new zigux/kernel starter relays may land only when the same bounded change also refreshes this note, the shared ABI slice, and the manifest-backed Phase 3 packet inventory.`
- keep `zigux/kernel/export_shim.zig` as a thin kernel-facing relay over already-owned ABI and UAPI surfaces rather than a second semantic home for header layout, enum ownership, or low-level helper policy
- new kernel-facing wrapper names without matching shared replay or manifest-backed evidence should be treated as churn, not Phase 3 closure
- repetitive suffix-chain relay growth inside `zigux/kernel/` does not count as product progress on its own

## Current State

- live `zigux/kernel/export_shim.zig` re-exports the shipped `Header`, `HeaderCompatibility`, `HeaderAcceptance`, and `HeaderEvaluation` types from `zigux/uapi/version.zig`, and now also keeps the kernel-facing `CompatibilityDecision`, `DeviceEncodingResult`, and `DeviceNumber` relay shapes explicit for callers that need the requested value, the tagged status packet, or a decoded `dev_t` view together
- live `zigux/kernel/export_shim.zig` keeps the shared boundary-header constructor family readable through `versionedHeader()`, `canonicalHeader()`, `boundaryHeader()`, `compatibleHeader()`, and `header()` instead of forcing kernel-side callers to reach around the starter relay for those constructor details
- live `zigux/kernel/export_shim.zig` keeps ABI-version, size, and acceptance predicates reviewable through `isCurrentAbiVersion()`, `isCompatibleSize()`, `isCanonicalSize()`, `headerCompatibility()`, `acceptHeader()`, `isCompatibleHeader()`, `isCanonicalHeader()`, and `canonicalizeHeader()` so the kernel-facing packet still mirrors the shipped starter compatibility rules rather than inventing a second ownership home
- live `zigux/kernel/export_shim.zig` keeps status shaping and success-versus-error checks reviewable through `ok()`, `errno()`, `normalize()`, and `isOk()` instead of leaving export-status interpretation implicit in broader helper or header growth
- live `zigux/kernel/export_shim.zig` keeps accepted-header relay state explicit through `evaluateHeader()`, `compatibilityStatus()`, `extendsBoundary()`, and `requestedExtraBytes()` so kernel-facing callers can stay on the shared boundary-header contract without inventing a second ABI home
- live `zigux/kernel/export_shim.zig` also exposes status-tagged `encodeDeviceNumber()` and `lastDeviceNumberInRange()` relays plus the pure `decodeDeviceNumber()` view over the shipped `zigux/uapi/dev_t.zig` starter companion without re-homing `dev_t` ownership into `zigux/kernel/`
- current `master` still ships no wider `zigux/kernel/` family beyond this starter relay, so the honest next step remains keeping this ownership note aligned with the relay surface that already exists rather than growing more kernel-surface names

## Boundary

- this note does not move starter UAPI ownership out of `zigux/uapi/`
- this note does not move Linux-facing aggregation ownership out of `include/linux/zigux.h`
- this note does not move canonical ABI layout or compatibility semantics out of `include/zigux/abi.h` or `zigux/uapi/version.zig`
- this note does not authorize deeper kernel-port claims, driver shims, or low-level helper growth under `zigux/kernel/`
- if a future bounded change adds another kernel-facing substrate relay, refresh this note together with `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-abi-slice.md`, and `zigux/tests/fixtures/phase3_abi_manifest.json` in the same packet so the kernel-facing side of the boundary stays explicit

## Maintenance-Mode Handoff

- reopen `P3-Y07` only when `zigux/kernel/export_shim.zig` adds, removes, or rehomes a kernel-facing relay, or when this note stops matching `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-abi-slice.md`, or `zigux/tests/fixtures/phase3_abi_manifest.json` about the kernel-facing ownership split
- before trusting a reopened packet, reread `zigux/kernel/export_shim.zig` together with `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, `Documentation/zigux/phase3-abi-slice.md`, and `zigux/tests/fixtures/phase3_abi_manifest.json`
- keep the next bounded step to one same-packet note or manifest correction unless a real kernel-facing starter relay lands in `zigux/kernel/export_shim.zig`
- if repo drift is only about starter UAPI wording, Linux-facing header aggregation, helper policy, or low-level wrapper proof, leave this lane parked and route the follow-up to `P3-Y02`, `P3-Y05`, `P3-Y04`, or `P3-Y03` instead of reopening kernel-facing governance by habit

## Non-Goals

- this note does not claim new UAPI companions
- this note does not claim new bindings or header families
- this note does not claim runtime scheduler, workqueue, RCU, or driver-port progress
