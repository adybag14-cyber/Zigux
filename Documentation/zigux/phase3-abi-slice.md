# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the bounded Phase 3 starter packets, the layout-assert-backed shared ABI replay surface, the low-level wrapper reminder surface, the focused policy starter packet, the Linux-facing header governance companion, the dedicated adjacent support-packet guard, and the direct export/UAPI C-header smoke route are reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=current master now carries one bounded starter header-family packet plus three directly readable starter bindings, one directly readable starter export shim companion built on the shared ABI binding surface, one focused export-or-UAPI layout replay companion, one focused export-or-UAPI C-header smoke route, one separate focused policy helper slice plus one directly readable policy starter packet and manifest-backed replay companion that reuse the shared ABI bindings, one directly readable layout-assert helper companion, one directly readable shared ABI header plus three directly readable shared ABI bindings with starter header-family relay evidence, chrdev layout-and-constant evidence, and notifier layout-plus-helper evidence, one directly readable shared ABI core replay companion, one directly readable shared ABI dump companion, one directly readable Phase 3 catalog helper, one directly readable export-or-UAPI survey validator, one directly readable header-family survey validator, one directly readable Linux-facing header governance validator, one manifest-backed shared ABI inventory companion, one dedicated shared ABI catalog-selftest guard, one dedicated adjacent shared ABI support-packet guard, one dedicated shared ABI header-family survey note, and one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, one directly readable barrier helper companion, one directly readable MMIO helper companion, one directly readable helper-local unsafe-policy companion, the shared unsafe-scope decoder, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one returned Makefile replay gate, and one workflow-backed replay route`
- `PHASE3_CURRENT_INTEROP_GAP=current master now materializes one Linux-facing header pair, two starter UAPI companion files, four directly readable starter bindings, one starter export shim companion, one focused export-or-UAPI layout replay route, one direct export/UAPI C-header smoke route, one shared ABI validator entrypoint, one directly readable layout-assert helper companion, one shared ABI header, three shared ABI bindings, one directly readable shared ABI core replay route, one directly readable shared ABI dump route, one directly readable Phase 3 catalog helper, one directly readable shared ABI catalog-selftest guard, one dedicated adjacent shared ABI support-packet guard, one directly readable export/UAPI survey validator, one directly readable header-family survey validator, one directly readable Linux-facing header governance validator, one manifest-backed shared ABI inventory companion, one separate focused policy helper slice plus one focused policy starter packet and manifest-backed replay route built on shared ABI bindings, one focused starter replay route, one dedicated header-family survey note, and one adjacent low-level-wrapper reminder surface built around zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/Makefile, and .github/workflows/zigux-bootstrap.yml, while broader later Phase 3 routes remain outside this bounded packet`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=direct GitHub readback on 2026-05-21 now reaches the starter header-family packet on master at include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/dev_t.zig, zigux/uapi/version.zig, zigux/bindings/dev_t.zig, zigux/bindings/version.zig, zigux/bindings/header_family.zig, zigux/bindings/abi.zig, zigux/kernel/export_shim.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig; it also reaches the shared ABI evidence packet through Documentation/zigux/phase3-policy-slice.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, include/zigux/abi.h, zigux/bindings/abi.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/layout_assert.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/unsafe_policy.zig, zigux/tests/phase3_abi.zig, zigux/tests/build.zig, zigux/tests/phase3_abi_dump_current.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-support-packet.py, scripts/zigux/validate-phase3.py, scripts/zigux/phase3_catalog.py, scripts/zigux/check-phase3-catalog-selftest.py, scripts/zigux/check-phase3-policy-starter-packet.py, scripts/zigux/check-phase3-export-uapi-c-header-smoke.py, scripts/zigux/validate-phase3-export-uapi-survey.py, scripts/zigux/validate-phase3-abi-header-family-survey.py, scripts/zigux/validate-phase3-linux-zigux-header-governance.py, and zigux/tests/fixtures/phase3_abi_manifest.json, with the shared dump route now keeping the MMIO unsafe-scope constant, the chrdev status and budget-window constants, and their layout offsets directly readable; it also reaches one focused export-or-UAPI layout replay through zigux/tests/phase3_export_uapi_layout.zig and zigux/tests/phase3_export_uapi_layout_build.zig, one direct export/UAPI C-header smoke route through zigux/tests/phase3_export_uapi_c_header_smoke.c, one focused policy starter packet through zigux/tests/phase3_policy_starter_packet.zig, zigux/tests/phase3_policy_starter_packet_build.zig, and zigux/tests/phase3_policy_starter_packet_manifest.json, one dedicated adjacent support-packet guard through python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test and python3 scripts/zigux/check-phase3-abi-support-packet.py, and one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/Makefile, and .github/workflows/zigux-bootstrap.yml. Earlier survey wording that the separate broader header-family binding follow-through remains the wider gap is now historical rather than current repo reality because zigux/bindings/header_family.zig and the focused replay route are both present on master.`

## Readable Reminder Surfaces

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
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
- `zigux/bindings/header_family.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/check-phase3-abi-support-packet.py`
- `scripts/zigux/phase3_catalog.py`
- `scripts/zigux/check-phase3-catalog-selftest.py`
- `scripts/zigux/check-phase3-policy-starter-packet.py`
- `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-linux-zigux-header-governance.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `zigux/tests/phase3_abi_dump_current.zig`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `zigux/tests/phase3_export_uapi_c_header_smoke.c`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-abi-support-packet.py`
- `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`
- `python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test`
- `python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py`
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`
- `zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-abi-core-packet --build-file zigux/tests/build.zig`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `make -C zigux phase3-low-level-wrappers-test`

## Current Gap

Current `master` still presents the honest same-lane outcome as a bounded starter-packet set plus a bounded shared ABI binding surface, a landed shared header-family binding relay, one focused export-or-UAPI layout replay, one direct export/UAPI C-header smoke route, one focused policy starter packet, one dedicated Linux-facing header governance companion, one dedicated adjacent support-packet guard, one dedicated header-family survey follow-through, and one bounded low-level-wrapper reminder surface, not as full Phase 3 completion.

The live shared packet now includes `zigux/bindings/header_family.zig` beside `zigux/bindings/abi.zig` and `zigux/bindings/notifier_abi.zig`, the directly readable layout-assert helper companion at `zigux/helpers/layout_assert.zig`, the shared ABI core replay in `zigux/tests/phase3_abi.zig`, the shared ABI dump route at `zigux/tests/phase3_abi_dump_current.zig`, the focused export-or-UAPI layout replay at `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, the direct C smoke proof at `zigux/tests/phase3_export_uapi_c_header_smoke.c` plus `scripts/zigux/check-phase3-export-uapi-c-header-smoke.py`, the focused policy starter packet at `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, and `scripts/zigux/check-phase3-policy-starter-packet.py`, the manifest-backed shared ABI inventory at `zigux/tests/fixtures/phase3_abi_manifest.json`, the shared validator entrypoint plus shared ABI checker in `scripts/zigux/validate-phase3.py` and `scripts/zigux/check-phase3-abi.py`, the directly readable catalog helper plus returned catalog-selftest guard in `scripts/zigux/phase3_catalog.py` and `scripts/zigux/check-phase3-catalog-selftest.py`, the dedicated adjacent support-packet guard in `scripts/zigux/check-phase3-abi-support-packet.py`, the directly readable export/UAPI survey validator in `scripts/zigux/validate-phase3-export-uapi-survey.py`, the dedicated header-family survey follow-through in `Documentation/zigux/phase3-abi-header-family-survey.md` plus `scripts/zigux/validate-phase3-abi-header-family-survey.py`, the returned Linux-facing header governance companion in `Documentation/zigux/phase3-linux-zigux-header-governance.md` plus `scripts/zigux/validate-phase3-linux-zigux-header-governance.py`, and the adjacent low-level-wrapper reminder surface in `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.

That reminder surface keeps the landed header-family binding relay, one directly readable layout-assert helper companion, the focused policy starter packet, the direct export/UAPI C smoke proof, one directly readable MMIO helper companion, the directly coupled helper-local `zigux/helpers/unsafe_policy.zig` companion, the shared unsafe-scope decoder in `zigux/unsafe/narrow.zig`, the manifest-backed shared ABI inventory companion, the shared validator entrypoint, the shared ABI checker, the Phase 3 catalog helper, the returned catalog-selftest guard, the dedicated adjacent support-packet guard, the export/UAPI survey validator, the dedicated header-family survey validator, the dedicated Linux-facing header governance validator, the dedicated header-family survey note, the returned Linux-facing header governance companion, the dedicated low-level-wrapper survey validator, the focused replay shard, the dedicated shared build companion, the returned Makefile replay gate, and the workflow-backed replay route explicit without implying that the broader unfinished Phase 3 routes already ship.

## Scope

This note is limited to repo-reality reporting for the shared Phase 3 ABI lane. It records one directly readable starter header-family packet, the starter bindings, the landed header-family binding relay, the starter export shim companion, the shared ABI validator entrypoint, the shared ABI header plus both shared ABI binding files and the header-family relay binding, the directly readable layout-assert helper companion, the shared ABI core replay and dump routes, the shared build route, the manifest-backed shared ABI inventory, the focused export-or-UAPI layout replay, the direct export/UAPI C-header smoke route, the directly readable Phase 3 catalog helper, the returned catalog-selftest guard, the dedicated adjacent support-packet guard, the directly readable export/UAPI survey validator, the focused policy starter packet and manifest-backed replay companion, the dedicated Linux-facing header governance validator, the dedicated header-family survey follow-through, the returned Linux-facing header governance companion, and the separate low-level-wrapper reminder surface that now includes the helper-local unsafe-policy companion, the shared unsafe-scope decoder, the focused replay shard, the dedicated shared build companion, the returned Makefile replay gate, and the workflow-backed replay route. It does not claim that broader later Phase 3 routes already ship on current `master`.
