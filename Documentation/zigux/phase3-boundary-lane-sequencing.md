# Phase 3 Boundary Lane Sequencing

This note records the current scripts-root sequencing boundary for the bounded Phase 3 ABI packet on `master`.

## Current Status

- `PHASE3_BOUNDARY_LANE_SCOPE=keep the live Phase 3 ABI lane anchored to the directly readable starter dev_t packet, the focused err_ptr/xarray helper slice, the directly readable xarray_slot starter packet, the focused policy slice, the bounded low-level-wrapper survey-and-replay packet, the adjacent export/UAPI layout replay pair, the linux-facing header governance note, the shared ABI catalog helper plus manifest-backed inventory, and the shared scripts-root validator packet instead of widening into the older export/UAPI survey, catalog-selftest, or broader ABI validator family`
- `PHASE3_BOUNDARY_LANE_DETAIL=direct current-head readback on 2026-05-19 reaches Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-errptr-xarray-slice.md, Documentation/zigux/phase3-policy-slice.md, Documentation/zigux/phase3-validator-support-surface.md, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/kernel/export_shim.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/helpers/xarray_slot_view.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, zigux/tests/phase3_xarray_slot_starter_packet.zig, zigux/tests/build.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/phase3_export_uapi_layout.zig, zigux/tests/phase3_export_uapi_layout_build.zig, scripts/zigux/check-phase3-selftest-surface.py, scripts/zigux/check-phase3-readme-tooling-inventory.py, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3-validator-support-surface.py, scripts/zigux/validate_phase3_selftest.py, scripts/zigux/run-phase3-checks.py, scripts/zigux/validate-phase3.py, scripts/zigux/phase3_catalog.py, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, and zigux/tests/fixtures/phase3_abi_manifest.json, while repeated authenticated contents reads still return missing for the catalog-selftest route and the broader header-family reminder notes`
- `PHASE3_BOUNDARY_LANE_NEXT_STEP=keep follow-through inside one scripts-root inventory, validator, manifest, or directly coupled reminder-surface truthfulness repair at a time; keep low-level-wrapper helper-local barrier follow-through on P3-L20 separate from low-level-wrapper validator-or-replay maintenance on P3-L24; if a broader Phase 3 route is still missing on current master, record it as a repo-reality gap instead of treating it as shipped boundary evidence`

## Roadmap And Ledger Anchors

- The Phase 3 roadmap keeps `ABI/export surfaces`, `allocators`, `atomics and barriers`, and `MMIO` inside the bounded ABI and interop substrate.
- Bootstrap ledger step `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, still names the same core boundary family through `include/zigux/abi.h`, `include/linux/zigux.h`, `zigux/bindings/abi.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/kernel/export_shim.zig`, `zigux/unsafe/narrow.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3.py`, and `Documentation/zigux/phase3-abi-slice.md`.

## Current Directly Readable Boundary Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/kernel/export_shim.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/bindings/abi.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/build.zig`
- `zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `scripts/zigux/check-phase3-selftest-surface.py`
- `scripts/zigux/check-phase3-readme-tooling-inventory.py`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `scripts/zigux/validate_phase3_selftest.py`
- `scripts/zigux/run-phase3-checks.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/phase3_catalog.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

## Sampled Wider Gaps Still Absent On Current `master`

- `scripts/zigux/check-phase3-catalog-selftest.py`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`

## Current Gap

Current Phase 3 follow-through is a boundary-discipline problem, not a license to widen the ABI packet. The live tree now carries enough directly readable starter, helper-local, xarray-slot, policy, low-level-wrapper, adjacent export/UAPI reminder, linux-facing header governance, shared ABI catalog helper, manifest-backed ABI inventory, layout replay, and scripts-root validator surfaces to keep one bounded review packet honest. That still does not justify broader catalog-selftest or replay claims, and the readable export/UAPI survey note plus its packet-local validator and the linux-facing header governance note should stay treated as adjacent reminder surfaces rather than as proof that the wider shared ABI validator family has returned.

That means the safe same-lane sequencing rule is to keep Phase 3 work on directly coupled truthfulness, manifest, validator, or reminder repairs inside the already materialized packet. Missing broader Phase 3 routes should stay framed as repo-reality gaps until the files actually return on `master`.

## Scope

This note is limited to scripts-root sequencing guidance for the current bounded Phase 3 ABI packet. It records the directly readable starter, helper-local, xarray-slot starter, policy, low-level-wrapper, adjacent export/UAPI reminder, linux-facing header governance, shared ABI catalog helper, manifest-backed ABI inventory, packet-local validator and layout replay, validator-support, and shared-ABI-validator surfaces; names sampled broader routes that remain absent; and keeps the next bounded step narrow. It does not claim that the broader Phase 3 ABI validator family, catalog-selftest wiring, or focused low-level-wrapper replay companions already ship on current `master`, and it keeps the readable export/UAPI survey note plus its packet-local validator and the linux-facing header governance note classified as reminder surfaces rather than wider shared ABI validator proof.