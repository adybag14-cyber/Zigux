# Phase 3 Policy Slice

This note records the current helper-local Phase 3 policy slice on `master`.

## Current Status

- `PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, three helper-local decoders, one reusable layout guard, one cross-check narrow-surface decoder, one machine-readable manifest, and one focused replay route`
- `PHASE3_POLICY_SLICE_SCOPE=this slice proves shared InteropPolicy layout assertions, panic escalation, allocator-init ownership, and unsafe-scope reviewability by cross-checking the helper-local decoder against zigux/unsafe/narrow.zig, including the unsafe helper's newer scope-and-permits symmetry aliases, without widening into unsafe wrappers, runtime shims, or broader export-boundary claims`
- `PHASE3_POLICY_NEXT_SAFE_STEP=keep policy helper coverage bounded to layout assertions, manifest-backed replay, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families`

## Files Present On Master

- `Documentation/zigux/phase3-policy-slice.md`
- `include/zigux/abi.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`

## Current Gap

The Phase 3 roadmap still leaves broader runtime-shim and shared ABI replay surfaces unfinished. This slice only proves that the shared `zigux_interop_policy` layout already present in `include/zigux/abi.h`, `zigux/bindings/abi.zig`, and the shared `zigux/bindings/notifier_abi.zig` companion can be checked consistently by the existing `layout_assert`, `panic_policy`, `allocator_policy`, and `unsafe_policy` helpers under one manifest-backed replay route, with `zigux/unsafe/narrow.zig` kept as a bounded same-lane cross-check for the narrow unsafe decode surface.

That makes the slice a real review surface, not a completion claim. Current `master` still carries the older `zigux/unsafe/narrow.zig` helper, but this focused starter packet now treats that file as a bounded proof companion rather than as an out-of-band background file: the helper-local `zigux/helpers/unsafe_policy.zig` decoder remains the main replay route, while the dedicated `layout_assert` checks keep `InteropPolicy` field layout explicit and the narrow decoder is only used to confirm the same unsafe-scope decisions without widening into wrapper, MMIO, or runtime behavior proof. This note still does not imply that `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `scripts/zigux/check-phase3-abi.py`, or `scripts/zigux/validate-phase3.py` already ship on `master`, even though the adjacent export/UAPI layout replay pair at `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig` is separately present on current `master`.

## Scope

This note is limited to the focused policy helper family. It records the directly readable ABI bindings, the helper-local policy decoders, the reusable `layout_assert` guard, the bounded narrow-surface cross-check companion, the dedicated replay route, and the machine-readable manifest. It does not claim broader shared ABI replay, export-boundary, runtime-shim, or MMIO or wrapper completion. The dedicated replay here is only meant to keep the layout, panic, allocator, and unsafe helper contracts explicit while the wider Phase 3 packet remains unfinished.
