# Phase 3 Policy Slice

This note records the current helper-local Phase 3 policy slice on `master`.

## Current Status

- `PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, three helper-local decoders, one machine-readable manifest, and one focused replay route`
- `PHASE3_POLICY_SLICE_SCOPE=this slice proves shared interop-policy decoding for panic escalation, allocator-init ownership, and unsafe-scope reviewability without widening into unsafe wrappers, runtime shims, or broader export-boundary claims`
- `PHASE3_POLICY_NEXT_SAFE_STEP=keep policy helper coverage bounded to manifest-backed replay and truthful reminder surfaces before widening into mmio, low-level wrapper, or shared runtime-shim families`

## Files Present On Master

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
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

The Phase 3 roadmap still leaves broader runtime-shim and unsafe-boundary surfaces unfinished. This slice only proves that the shared `zigux_interop_policy` layout already present in `include/zigux/abi.h` and `zigux/bindings/abi.zig` can be decoded consistently by the existing `panic_policy`, `allocator_policy`, and `unsafe_policy` helpers under one manifest-backed replay route.

That makes the slice a real review surface, not a completion claim. It does not imply that `zigux/unsafe/narrow.zig`, `zigux/helpers/mmio.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/atomic.zig`, `zigux/kernel/export_shim.zig`, or shared Phase 3 validator routes already ship on `master`.

## Scope

This note is limited to the focused policy helper family. It records the directly readable ABI binding, the helper-local policy decoders, the dedicated replay route, and the machine-readable manifest. It does not claim broader runtime-shim, unsafe-wrapper, or export-boundary completion.
