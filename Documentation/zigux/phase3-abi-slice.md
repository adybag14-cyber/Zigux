# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the bounded Phase 3 starter packets and low-level wrapper reminder surface are reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet plus two directly readable starter bindings, one directly readable starter export shim companion built on the shared ABI binding surface, one focused export-or-UAPI layout replay companion, one separate focused policy helper slice that reuses the shared ABI bindings, one directly readable shared ABI header plus two directly readable shared ABI bindings with chrdev layout-and-constant evidence and notifier layout-plus-helper evidence, one directly readable shared ABI core replay companion, one directly readable shared ABI dump companion, one directly readable Phase 3 catalog helper, one directly readable export-or-UAPI survey validator, one manifest-backed shared ABI inventory companion, one dedicated shared ABI catalog-selftest guard, and one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, one directly readable barrier helper companion, one directly readable MMIO helper companion, one directly readable helper-local unsafe-policy companion, the shared unsafe-scope decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, and one dedicated shared build companion`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair, two starter UAPI companion files, three directly readable starter bindings, one starter export shim companion, one focused export-or-UAPI layout replay route, one shared ABI validator entrypoint, one shared ABI header, two shared ABI bindings, one directly readable shared ABI core replay route, one directly readable shared ABI dump route, one directly readable Phase 3 catalog helper, one directly readable shared ABI catalog-selftest guard, one directly readable export-or-UAPI survey validator, one manifest-backed shared ABI inventory companion, one separate focused policy helper slice built on shared ABI bindings, one focused starter replay route, and one adjacent low-level-wrapper reminder surface built around zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig, while the still-missing broader header-family survey follow-through remains the separate wider gap`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-19 now reaches the starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/abi.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig; it also reaches the shared ABI evidence packet through Documentation/zigux/phase3-policy-slice.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_abi.zig, zigux/tests/build.zig, zigux/tests/phase3_abi_dump_current.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3.py, scripts/zigux/phase3_catalog.py, scripts/zigux/check-phase3-catalog-selftest.py, scripts/zigux/validate-phase3-export-uapi-survey.py, and zigux/tests/fixtures/phase3_abi_manifest.json, with the shared dump route now keeping the MMIO unsafe-scope constant, the chrdev status and budget-window constants, and their layout offsets directly readable; it also reaches one focused export-or-UAPI layout replay through zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig; it separately reaches the returned linux-header governance companion through Documentation/zigux/phase3-linux-zigux-header-governance.md; and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; representative broader Phase 3 paths still remain absent, including scripts/zigux/validate-phase3-abi-header-family-survey.py and Documentation/zigux/phase3-abi-header-family-survey.md`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
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
- `scripts/zigux/check-phase3-catalog-selftest.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `zigux/tests/phase3_abi_dump_current.zig`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-abi-core-packet --build-file zigux/tests/build.zig`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

## Current Gap

Current `master` still presents the honest same-lane outcome as a bounded starter-packet set plus a bounded shared ABI binding surface, one focused export-or-UAPI layout replay, and one bounded low-level-wrapper reminder surface, not as full Phase 3 completion. The shared ABI packet now includes both `zigux/bindings/abi.zig` and `zigux/bindings/notifier_abi.zig`, the directly readable shared ABI core replay in `zigux/tests/phase3_abi.zig`, the shared ABI dump route in `zigux/tests/phase3_abi_dump_current.zig`, the shared build routing in `zigux/tests/build.zig`, the manifest-backed shared ABI inventory in `zigux/tests/fixtures/phase3_abi_manifest.json`, the shared validator entrypoint plus shared ABI checker in `scripts/zigux/validate-phase3.py` and `scripts/zigux/check-phase3-abi.py`, the directly readable catalog helper plus returned catalog-selftest guard in `scripts/zigux/phase3_catalog.py` and `scripts/zigux/check-phase3-catalog-selftest.py`, the directly readable export/UAPI survey validator in `scripts/zigux/validate-phase3-export-uapi-survey.py`, and the returned linux-header governance companion in `Documentation/zigux/phase3-linux-zigux-header-governance.md`.

That newer starter-boundary evidence still belongs to ledger entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, even though current `master` no longer uses the older `zigux/tests/phase3_abi_dump.zig` path from that bootstrap list verbatim. The live shared replay now runs through `zigux/tests/phase3_abi.zig`, the shared dump route now lives at `zigux/tests/phase3_abi_dump_current.zig` and directly keeps the MMIO unsafe-scope constant plus the chrdev status and budget-window constants readable, the shared Phase 3 test routing now lives in `zigux/tests/build.zig`, and the manifest-backed ABI inventory now lives at `zigux/tests/fixtures/phase3_abi_manifest.json`.

That reminder surface keeps one directly readable MMIO helper companion, the directly coupled helper-local `zigux/helpers/unsafe_policy.zig` companion, the manifest-backed shared ABI inventory companion, the shared validator entrypoint, the shared ABI checker, the Phase 3 catalog helper, the returned catalog-selftest guard, the export/UAPI survey validator, the returned linux-header governance companion, the dedicated survey validator, the focused replay shard, and the dedicated shared build companion explicit without implying that the broader header-family survey follow-through already ships. Review shorthand for this bounded packet: the shared ABI lane should keep the live replay routes, dump route, manifest inventory, checker, validator, catalog helper, returned catalog-selftest guard, and directly coupled broader header-family follow-through gaps explicit until those remaining Phase 3 routes materialize.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records one directly readable starter header-family packet, the starter bindings, the starter export shim companion, the shared ABI validator entrypoint, the shared ABI header plus both shared ABI binding files, the shared ABI core replay and dump routes, the shared build route, the manifest-backed shared ABI inventory, the focused export-or-UAPI layout replay, the directly readable Phase 3 catalog helper, the returned catalog-selftest guard, the directly readable export/UAPI survey validator, the returned linux-header governance companion, the separate focused policy slice, and the adjacent low-level-wrapper reminder surface; names the broader header-family survey follow-through that remains absent; and preserves a narrow next-step recommendation. It does not claim that those remaining broader routes already ship on current `master`.