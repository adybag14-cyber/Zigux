# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current roadmap-versus-repo reality for the Phase 3 low-level wrapper family on `master`.

## Current Status

- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, but current master does not yet materialize that helper trio or the focused replay and survey packet that earlier continuity notes described`
- `PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback on 2026-05-17 reaches the bounded Phase 3 starter, helper-local err_ptr/xarray, and focused policy slices, while repeated authenticated contents reads return missing for zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, and Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md before this note landed`
- `PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through in survey-and-gap-accounting mode until current master actually materializes one bounded helper or focused replay surface; the next honest implementation step would be the first directly readable atomic, barrier, or MMIO helper shard together with one equally bounded proof route`

## Roadmap And Ledger Anchors

- The Phase 3 roadmap still names `approved atomic, barrier, and MMIO wrappers` as required Zigux features inside the ABI and interop substrate.
- Bootstrap ledger step `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, still lists `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3.py`, and `Documentation/zigux/phase3-abi-slice.md` as part of that original bounded Phase 3 substrate packet.

## Current Directly Readable Phase 3 Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-shared-reminder-gap.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`

## Missing Low-Level Wrapper Surfaces On Current `master`

- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

## Current Gap

The live Phase 3 tree is not empty. It already exposes the bounded starter packet, the focused helper-local `err_ptr` and `xarray` slice, and the focused policy slice. What it does not currently expose is the separate low-level wrapper family that the roadmap and ledger still reserve.

That makes the real same-lane outcome a survey-first truthfulness repair, not another speculative helper edit. Reviewers should treat atomic, barrier, and MMIO wrappers as an open Phase 3 gap on current `master` until at least one helper shard and one matching proof route become directly readable again.

## Scope

This note is limited to roadmap-versus-repo-reality accounting for the low-level wrapper family. It records the current directly readable Phase 3 packet, names the missing atomic, barrier, and MMIO wrapper surfaces, and keeps the next bounded implementation step explicit. It does not claim that the broader low-level wrapper packet, shared ABI replay, or validator stack already ships on current `master`.