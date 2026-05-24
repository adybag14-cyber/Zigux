# Phase 3 Kernel Export Shim Governance

This note records the current kernel-facing ownership boundary for `zigux/kernel/export_shim.zig` on `master`.

## Current Status

- `PHASE3_KERNEL_EXPORT_SHIM_SCOPE=current master now exposes one bounded kernel-facing export shim companion that keeps Phase 3 relay ownership explicit for public relay types, exported boundary constants, boundary-header constructors and predicates, status-tagged boundary-header compatibility validation, starter version component predicates plus whole-version forwarding, status-tagged version and dev_t validation, the bounded device-number bridge, and the dedicated focused export-shim replay handoff without widening into broader runtime-shim or helper-family claims`
- `PHASE3_KERNEL_EXPORT_SHIM_FILE_SET=direct current-head readback on 2026-05-23 reaches zigux/kernel/export_shim.zig, zigux/bindings/abi.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/tests/phase3_export_shim_build.zig, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_KERNEL_EXPORT_SHIM_NEXT_SAFE_STEP=keep follow-through bounded to one kernel-facing ownership note or directly coupled export-shim or export-uapi layout proof refresh at a time; do not widen into shared ABI manifests, linux header governance, broader export-uapi survey work, or low-level-wrapper maintenance from this packet`

## Current Kernel-Facing Relay Surface

- `BoundaryHeader`, `ExportStatus`, `Facility`, `Version`, and `DevTFields` keep the kernel-facing relay result shapes, enum tags, and field layout ownership explicit inside `zigux/kernel/export_shim.zig` instead of leaving those public packet types implied by wider ABI notes.
- `abi_version` and `header_size` keep the shared boundary-header contract pinned to exported kernel-facing constants that the focused layout replay can compare directly without rebuilding that ownership elsewhere.
- `canonicalHeader(flags)` owns the bounded constructor path for the shared `BoundaryHeader` shape.
- `isCurrentAbiVersion`, `isCanonicalSize`, `isCompatibleSize`, `headerIsCanonical`, `headerIsCompatible`, `extendsBoundary`, `requestedExtraBytes`, `canonicalizeHeader`, and `validateBoundaryHeader` keep the starter header-compatibility contract reviewable inside the kernel-facing shim.
- `currentVersion()`, `hasCurrentAbiMajor()`, `hasCurrentAbiMinor()`, `hasCurrentHeaderFamilyRevision()`, `versionMatchesCurrent()`, and `validateVersion()` keep the starter version relay and compatibility gate explicit through the shared `zigux/bindings/version.zig` surface, with `validateVersion()` now delegating to the UAPI-backed status-tagged validator instead of rebuilding that status locally.
- `makeDevTFields`, `encodeDeviceNumber`, `decodeDeviceNumber`, `validateDeviceFields`, `validateDeviceNumber`, and `validateDeviceRange` keep bounded `dev_t` field forwarding, device-number bridging, and validation tied to the kernel-facing shim rather than spread across unrelated helper packets.
- `okStatus`, `errorStatus`, and `statusIsOk` keep facility-tagged export status handling explicit for the same starter relay packet.

## Files Present On Master

- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `zigux/kernel/export_shim.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/tests/phase3_export_shim_build.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`

## Current Gap

The honest same-lane gap on current `master` is no longer the absence of a dedicated kernel-facing note. That ownership note already ships here beside `zigux/kernel/export_shim.zig`, and the directly coupled focused `phase3_export_shim_build` replay handoff plus the `phase3_export_uapi_layout` replay pair already keep the shim reviewable on bounded test routes.

The remaining packet-local risk is note drift. If `zigux/kernel/export_shim.zig` adds, removes, or renames public relay types, exported constants, constructor, predicate, version, status, or bounded `dev_t` relays, this note should be refreshed in the same bounded change so review stays anchored to the shim itself instead of silently falling back to wider ABI, export-uapi, or shared reminder packets.

## Scope

This note is limited to the kernel-facing export shim packet. It records the live relay families owned by `zigux/kernel/export_shim.zig`, the directly coupled bindings and UAPI companions it reads through, and the focused export-shim plus layout replay routes that keep the packet reviewable. It does not claim broader shared ABI validator, manifest, linux-header-governance, or low-level-wrapper completion.
