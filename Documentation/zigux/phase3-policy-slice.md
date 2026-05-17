# Phase 3 Policy Slice

This note records the current helper-local Phase 3 policy slice on `master`.

## Current Status

- `PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, two helper-local decoders, one machine-readable manifest, one focused replay route, and one adjacent unsafe-scope decoder`
- `PHASE3_POLICY_SLICE_SCOPE=this slice proves shared interop-policy decoding for panic escalation and allocator-init ownership while staying adjacent to the already landed unsafe-scope decoder without widening into MMIO wrappers, runtime shims, or broader export-boundary claims`
- `PHASE3_POLICY_NEXT_SAFE_STEP=keep the policy helper family bounded to manifest-backed replay and truthful reminder surfaces before widening the already landed unsafe decoder into MMIO or runtime-shim families`

## Files Present On Master

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`

## Current Gap

The Phase 3 roadmap still leaves broader runtime-shim and low-level-wrapper surfaces unfinished. This slice proves that the shared `zigux_interop_policy` layout already present in `include/zigux/abi.h` and `zigux/bindings/abi.zig` can be decoded consistently by the existing `panic_policy` and `allocator_policy` helpers under one manifest-backed replay route, while the adjacent `zigux/unsafe/narrow.zig` decoder shows that the unsafe-scope constants themselves are already materialized on `master`.

That makes the slice a real review surface, not a completion claim. It does not imply that manifest-backed unsafe replay, `zigux/helpers/mmio.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/atomic.zig`, `zigux/kernel/export_shim.zig`, or shared Phase 3 validator routes already ship on `master`.

## Scope

This note is limited to the focused policy helper family. It records the directly readable ABI binding, the helper-local policy decoders, the dedicated replay route, the machine-readable manifest, and the adjacent unsafe decoder that shares the same interop-policy constants. It does not claim broader runtime-shim, unsafe-wrapper replay, or export-boundary completion.
