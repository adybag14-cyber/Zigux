# Phase 3 ABI Slice

This note keeps the current Phase 3 ABI and binding boundary explicit against live `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded header-family packet, two directly readable binding surfaces, one focused policy replay packet, one focused dev_t starter packet, and one adjacent unsafe-scope decoder instead of the earlier smaller starter-only reminder`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes the Linux-facing header pair, the shared abi header, direct dev_t plus abi bindings, bounded policy and dev_t starter replays, and the adjacent unsafe-scope decoder, but it still lacks the broader export-shim, low-level-wrapper, and shared Phase 3 validator packet that the roadmap leaves for later substrate closure`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-17 reaches include/linux/zigux.h, include/zigux/dev_t.h, include/zigux/abi.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/bindings/abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/unsafe/narrow.zig, zigux/tests/phase3_dev_t_starter_packet.zig, zigux/tests/phase3_dev_t_starter_packet_build.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, scripts/zigux/check-phase3-dev-t-starter-packet.py, and scripts/zigux/check-phase3-policy-starter-packet.py on current master, while representative broader Phase 3 routes still remain absent, including zigux/helpers/layout_assert.zig, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_export_uapi_layout.zig, scripts/zigux/validate-phase3-export-uapi-survey.py, and scripts/zigux/validate-phase3.py`
- `PHASE3_NEXT_SAFE_STEP=keep Phase 3 narrowed to truthful reminder-surface maintenance and one bounded validator or wrapper proof at a time instead of widening the current header and binding packet into completion claims`

## Readable Boundary Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`

## Present Bounded Packet

- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`

## Remaining Sampled Gaps

- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3.py`

## Current Gap

The Phase 3 roadmap still calls for the permanent C/Zigux interop substrate: explicit exports, curated bindings, layout proofs, panic and allocator policy, approved low-level wrappers, and a narrow unsafe surface.

Current `master` now covers a real subset of that plan. Reviewers can inspect the Linux-facing header pair, the shared `abi` header, direct `dev_t` and `abi` bindings, a bounded policy replay packet, a bounded `dev_t` starter packet, and the adjacent unsafe-scope decoder on the live tree. That is real substrate progress, but it is not the broader export-boundary or low-level-wrapper packet yet.

The immediate truthfulness requirement is therefore to keep reminder surfaces aligned with this current packet and to add the next bounded validator or wrapper proof only when it lands directly on `master`. Do not describe the current header pair, bindings, policy replay, or unsafe decoder as if they already imply layout-assert, atomic, barrier, MMIO, export-shim, or shared validator completion.

## Scope

This note is limited to repo-reality reporting for the current Phase 3 ABI and binding boundary. It records the directly readable headers, bindings, bounded replay packets, and adjacent unsafe decoder that now ship on `master`, names a sampled set of broader substrate gaps that remain absent, and keeps the next safe step narrow. It does not claim that the wider Phase 3 export/UAPI layout, low-level-wrapper, or shared validator packet already ships.
