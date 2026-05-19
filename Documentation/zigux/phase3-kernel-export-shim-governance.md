# Phase 3 Kernel Export Shim Governance

This note records the current kernel-facing ownership boundary for `zigux/kernel/export_shim.zig` on `master`.

## Current Status

- `PHASE3_KERNEL_EXPORT_SHIM_SCOPE=current master now exposes one bounded kernel-facing export shim companion that keeps Phase 3 relay ownership explicit for boundary-header constructors and predicates, compatibility and canonicalization helpers, starter version and dev_t field forwarding, status-tagged version and dev_t validation, and the bounded device-number bridge without widening into broader runtime-shim or helper-family claims`
- `PHASE3_KERNEL_EXPORT_SHIM_FILE_SET=direct current-head readback on 2026-05-19 reaches zigux/kernel/export_shim.zig, zigux/bindings/abi.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/tests/phase3_export_uapi_layout.zig, and zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_KERNEL_EXPORT_SHIM_NEXT_SAFE_STEP=keep follow-through bounded to one kernel-facing ownership note or directly coupled export-uapi layout proof refresh at a time; do not widen into shared ABI manifests, linux header governance, broader export-uapi survey work, or low-level-wrapper maintenance from this packet`

## Current Kernel-Facing Relay Surface

- `canonicalHeader(flags)` owns the bounded constructor path for the shared `BoundaryHeader` shape.
- `isCurrentAbiVersion`, `isCanonicalSize`, `isCompatibleSize`, `headerIsCanonical`, `headerIsCompatible`, `extendsBoundary`, `requestedExtraBytes`, and `canonicalizeHeader` keep the starter header-compatibility contract reviewable inside the kernel-facing shim.
- `currentVersion()`, `versionMatchesCurrent()`, and `validateVersion()` keep the starter version relay and compatibility gate explicit through the shared `zigux/bindings/version.zig` surface.
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
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`

## Current Gap

The honest same-lane task on current `master` is ownership clarity, not broader Phase 3 expansion. `zigux/kernel/export_shim.zig` already carries a real kernel-facing relay surface, but that surface needs its own dedicated note so review stays anchored to the shim itself instead of being inferred indirectly from the wider ABI, export-uapi, or shared reminder packets.

That means this kernel-facing packet should stay limited to constructor, predicate, compatibility, version, status, and bounded `dev_t` relay ownership around `zigux/kernel/export_shim.zig` and the directly coupled `phase3_export_uapi_layout` replay pair. The note should not be used to imply that broader export-uapi survey routes, shared ABI validator stacks, or low-level-wrapper packets are complete just because the kernel-facing shim is present.

## Scope

This note is limited to the kernel-facing export shim packet. It records the live relay families owned by `zigux/kernel/export_shim.zig`, the directly coupled bindings and UAPI companions it reads through, and the focused layout replay route that keeps the packet reviewable. It does not claim broader shared ABI validator, manifest, linux-header-governance, or low-level-wrapper completion.
