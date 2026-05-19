# Phase 3 Policy Slice

This note records the current helper-local Phase 3 policy slice on `master`.

## Current Status

- `PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, three helper-local decoders, one reusable layout guard, one cross-check narrow-surface decoder, one machine-readable manifest, one focused self-check replay route, one focused dump replay route, one dump expectation fixture, and one dedicated dump validator`
- `PHASE3_POLICY_SLICE_SCOPE=this slice proves shared InteropPolicy layout assertions, panic escalation, allocator-init ownership, and unsafe-scope reviewability by cross-checking the helper-local decoder against zigux/unsafe/narrow.zig and by replaying one focused policy dump over the same bounded records without widening into unsafe wrappers, runtime shims, or broader export-boundary claims`
- `PHASE3_POLICY_NEXT_SAFE_STEP=keep policy helper coverage bounded to layout assertions, manifest-backed replay, focused dump replay, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families`

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
- `zigux/tests/phase3_policy_dump.zig`
- `zigux/tests/phase3_policy_dump_build.zig`
- `zigux/tests/fixtures/phase3_policy_dump_expected.txt`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `scripts/zigux/check-phase3-policy-dump.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-dump.py --self-test`
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`
- `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`

## Current Gap

The Phase 3 roadmap still leaves broader runtime-shim, catalog-selftest, and low-level-wrapper follow-through unfinished. This slice only proves that the shared `zigux_interop_policy` layout already present in `include/zigux/abi.h`, `zigux/bindings/abi.zig`, and the shared `zigux/bindings/notifier_abi.zig` companion can be checked consistently by the existing `layout_assert`, `panic_policy`, `allocator_policy`, and `unsafe_policy` helpers under one manifest-backed replay route, with `zigux/unsafe/narrow.zig` kept as a bounded same-lane cross-check for the narrow unsafe decode surface and one focused dump route that prints the same bounded policy records in a reviewer-readable form.

That makes the slice a real review surface, not a completion claim. Current `master` now separately serves the shared ABI core replay through `zigux/tests/phase3_abi.zig`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, and the shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, and it still serves the adjacent export/UAPI layout replay pair at `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`. This focused packet still keeps those broader shared ABI and export/UAPI surfaces adjacent rather than making them part of the helper-local policy slice: the helper-local `zigux/helpers/unsafe_policy.zig` decoder remains the main replay route, the dedicated `layout_assert` checks keep `InteropPolicy` field layout explicit, and the focused dump route at `zigux/tests/phase3_policy_dump.zig` replays the same policy choices without widening into wrapper, MMIO, or runtime behavior proof.

## Scope

This note is limited to the focused policy helper family. It records the directly readable ABI bindings, the helper-local policy decoders, the reusable `layout_assert` guard, the bounded narrow-surface cross-check companion, the dedicated self-check replay route, the focused dump replay route, the dump expectation fixture, and the machine-readable manifest. It does not claim broader shared ABI replay, export-boundary, runtime-shim, or MMIO or wrapper completion. The dedicated routes here are only meant to keep the layout, panic, allocator, and unsafe helper contracts explicit while the wider Phase 3 packet remains unfinished.
