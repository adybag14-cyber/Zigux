# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the bounded Phase 3 starter packets and low-level wrapper reminder surface are reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet plus two directly readable starter bindings, one directly readable starter export shim companion built on the shared ABI binding surface, one focused export-or-UAPI layout replay companion, one separate focused policy helper slice that reuses the shared ABI bindings, one directly readable shared ABI header plus two directly readable shared ABI bindings with chrdev layout evidence and notifier layout-plus-helper evidence, one directly readable shared ABI catalog route, and one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, one directly readable barrier helper companion, one directly readable MMIO helper companion, one directly readable helper-local unsafe-policy companion, the shared unsafe-scope decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair, two starter UAPI companion files, three directly readable starter bindings, one starter export shim companion, one focused export-or-UAPI layout replay route, one shared ABI validator entrypoint, one shared ABI header, two shared ABI bindings, one separate focused policy helper slice built on shared ABI bindings, one starter manifest, one focused starter replay route, and one adjacent low-level-wrapper reminder surface built around zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig, while the directly readable shared ABI checker and directly readable shared ABI catalog now sit beside that packet and the export/UAPI survey-validator route remains a separate gap`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-19 now reaches the starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig; it also reaches the shared ABI evidence packet through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, scripts/zigux/check-phase3-policy-starter-packet.py, and scripts/zigux/validate-phase3.py; it also reaches one focused export-or-UAPI layout replay through zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig; and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; it now also reaches scripts/zigux/check-phase3-abi.py and scripts/zigux/phase3_catalog.py, while representative broader Phase 3 paths still remain absent, including scripts/zigux/validate-phase3-export-uapi-survey.py`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/dev_t.zig`
- `zigux/uapi/version.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/phase3_catalog.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

## Current Gap

Current `master` still presents the honest same-lane outcome as a bounded starter-packet set plus a bounded shared ABI binding surface, one focused export-or-UAPI layout replay, and one bounded low-level-wrapper reminder surface, not as full Phase 3 completion. The shared ABI packet now includes both `zigux/bindings/abi.zig` and `zigux/bindings/notifier_abi.zig`, and the shared validator entrypoint, shared ABI checker, and shared ABI catalog route are directly readable through `scripts/zigux/validate-phase3.py`, `scripts/zigux/check-phase3-abi.py`, and `scripts/zigux/phase3_catalog.py`, while the export/UAPI survey validator still remains absent.

That newer starter-boundary evidence still belongs to ledger entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`: `include/linux/zigux.h`, `zigux/uapi/dev_t.zig`, the `zigux/tests/phase3_dev_t_starter_packet{,_build}.zig` pair, and the focused `zigux/tests/phase3_export_uapi_layout{,_build}.zig` replay extend the same bounded export shim and UAPI packet rather than opening a separate UAPI tranche.

That reminder surface keeps one directly readable MMIO helper companion, the directly coupled helper-local `zigux/helpers/unsafe_policy.zig` companion, the shared validator entrypoint, the shared ABI checker, the shared ABI catalog route, the dedicated survey validator, the focused replay shard, and the dedicated shared build companion explicit through `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` without implying that the export/UAPI survey-validator route already ships. Review shorthand for this bounded packet: the bounded low-level-wrapper reminder surface built around `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/unsafe/narrow.zig`, `scripts/zigux/validate-phase3.py`, the dedicated survey note, the dedicated survey validator, the focused replay shard, the dedicated shared build companion, and the direct replay command should stay explicit until broader Phase 3 routes materialize.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records one directly readable starter header-family packet, the starter bindings, the starter export shim companion, the shared ABI validator entrypoint, the shared ABI header plus both shared ABI binding files, the focused export-or-UAPI layout replay, the separate focused policy slice, the shared ABI catalog route, and the adjacent low-level-wrapper reminder surface; names the export/UAPI survey-validator route that remains absent; and preserves a narrow next-step recommendation. It does not claim that the export/UAPI survey-validator route already ships on current `master`.
