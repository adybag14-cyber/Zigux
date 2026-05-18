# Phase 3 Policy Slice

This note records the current helper-local Phase 3 policy slice on `master`.

## Current Status

- `PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, three helper-local decoders, one machine-readable manifest, and one focused replay route`
- `PHASE3_POLICY_SLICE_SCOPE=this slice proves shared interop-policy decoding for panic escalation, allocator-init ownership, and unsafe-scope reviewability, including the unsafe helper's newer scope-and-permits symmetry aliases, without widening into unsafe wrappers, runtime shims, or broader export-boundary claims`
- `PHASE3_POLICY_NEXT_SAFE_STEP=keep policy helper coverage bounded to manifest-backed replay and truthful reminder surfaces before widening into mmio, low-level wrapper, or shared runtime-shim families`

## Files Present On Master

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`

## Current Gap

The Phase 3 roadmap still leaves broader runtime-shim and shared ABI replay surfaces unfinished. This slice only proves that the shared `zigux_interop_policy` layout already present in `include/zigux/abi.h`, `zigux/bindings/abi.zig`, and the shared `zigux/bindings/notifier_abi.zig` companion can be decoded consistently by the existing `panic_policy`, `allocator_policy`, and `unsafe_policy` helpers under one manifest-backed replay route.

That makes the slice a real review surface, not a completion claim. Current `master` still carries the older `zigux/unsafe/narrow.zig` helper, but this focused starter packet no longer treats that file as the proof route for the lane; the narrow unsafe review surface here is the helper-local `zigux/helpers/unsafe_policy.zig` decoder plus `zigux/tests/phase3_policy_starter_packet.zig`, and that replay now proves both the original access-boundary entry points and the newer `scopeFromInteropPolicy` plus `permits*` symmetry layer on live interop-policy records. This note still does not imply that `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3.py`, or `zigux/tests/phase3_export_uapi_layout.zig` already ship on `master`.

## Scope

This note is limited to the focused policy helper family. It records the directly readable ABI bindings, the helper-local policy decoders, the dedicated replay route, and the machine-readable manifest. It does not claim that the older `zigux/unsafe/narrow.zig` helper is the active starter-packet proof surface, and it does not claim broader shared ABI replay, export-boundary, runtime-shim, or MMIO or wrapper completion. The dedicated replay here is only meant to keep the panic, allocator, and unsafe helper contracts explicit, including the unsafe helper's alias-symmetry entry points, while the wider Phase 3 packet remains unfinished.
