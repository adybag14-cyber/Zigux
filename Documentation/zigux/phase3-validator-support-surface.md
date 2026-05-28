# Phase 3 Validator Support Surface

This note records the current validator-facing Phase 3 surface on live `master`.

Current `master` now carries one bounded `dev_t` starter packet with paired `dev_t` and version bindings plus a directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` interop slice with both starter-packet and fixture-backed parity coverage, one focused helper-local `xarray_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage, one focused helper-local `idr_slot` classifier slice with both starter-packet and fixture-backed dump parity coverage, one bounded helper-local `bitmap` / `cpumask` starter slice with manifest-backed replay coverage, one bounded helper-local `list_head` / `hlist` starter-plus-dump slice with dedicated replay coverage, and one adjacent export/UAPI layout replay pair. It now separately ships the dedicated `Documentation/zigux/phase3-abi-header-family-survey.md` note together with `scripts/zigux/validate-phase3-abi-header-family-survey.py` as bounded header-family follow-through, plus the focused `Documentation/zigux/phase3-abi-h-boundary-next-step.md` note as the packet-local `include/zigux/abi.h` companion. It does not currently ship the broader shared Phase 3 replay packet itself, even though the shared `scripts/zigux/validate-phase3.py` validator entrypoint and `scripts/zigux/check-phase3-abi.py` shared ABI checker are directly readable on current `master`, current `master` also directly serves the bounded catalog helper at `scripts/zigux/phase3_catalog.py` together with the shared ABI manifest at `zigux/tests/fixtures/phase3_abi_manifest.json`, and the aligned docs-root, review-checklist, tests-root, and scripts-root reminder surfaces now keep that broader shared-summary drift closed.

Current `master` also directly serves the returned `Documentation/zigux/phase3-linux-zigux-header-governance.md` ownership note beside that adjacent export/UAPI layout replay pair, so the bounded Linux-facing relay is reviewable without turning this validator-support packet into the semantic owner of the separately landed header-family survey follow-through.

## Current starter packet present on `master`

- `Documentation/zigux/phase3-abi-slice.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all`

## Focused helper slice present on `master`

- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/phase3_errptr_xarray_dump_build.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray.py`
- `python3 scripts/zigux/check-phase3-errptr-xarray.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig`

## Focused xarray-slot slice present on `master`

- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --repo-root .`
- `zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/phase3_xarray_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `scripts/zigux/check-phase3-xarray-slot.py`
- `python3 scripts/zigux/check-phase3-xarray-slot.py --self-test`
- `python3 scripts/zigux/check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig`

## Focused idr-slot slice present on `master`

- `Documentation/zigux/phase3-idr-slot-slice.md`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_starter_packet.zig`
- `zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
- `scripts/zigux/check-phase3-idr-slot-starter-packet.py`
- `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root .`
- `zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zigux/tests/phase3_idr_slot_dump.zig`
- `zigux/tests/phase3_idr_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_idr_slot/expected.json`
- `scripts/zigux/check-phase3-idr-slot.py`
- `python3 scripts/zigux/check-phase3-idr-slot.py --self-test`
- `python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig`

## Focused bitmap/cpumask slice present on `master`

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py`
- `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

## Focused list/hlist slice present on `master`

- `Documentation/zigux/phase3-list-hlist-slice.md`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/tests/phase3_list_hlist_starter_packet.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_list_hlist_manifest.json`
- `scripts/zigux/check-phase3-list-hlist-starter-packet.py`
- `python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py`
- `zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/phase3_list_hlist_dump_build.zig`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `scripts/zigux/check-phase3-list-hlist.py`
- `python3 scripts/zigux/check-phase3-list-hlist.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig`

## Focused policy slice present on `master`

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
- `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_dump.zig`
- `zigux/tests/phase3_policy_dump_build.zig`
- `zigux/tests/fixtures/phase3_policy_dump_expected.txt`
- `scripts/zigux/check-phase3-policy-dump.py`
- `python3 scripts/zigux/check-phase3-policy-dump.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-dump.py`
- `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`

Current `master` also directly serves the same focused policy slice through the reviewer-readable dump route at `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts/zigux/check-phase3-policy-dump.py`, so the bounded policy packet now exposes both its starter replay and its focused dump companion without widening this note into MMIO, low-level-wrapper, or broader runtime-shim ownership.

## Adjacent export/UAPI layout replay present on `master`

- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`

## Review boundary

Keep the shared Phase 3 reminder packet anchored to those seven current-tree-backed slices until additional broader export/UAPI survey or shared replay proof lands.

Do not treat the current starter packet, its manifest-backed replay guard, its direct Zig compile replay, its starter export shim companion, its helper-local fixture-backed parity packet, the helper-local `xarray_slot` starter-plus-dump packet, the helper-local `idr_slot` starter-plus-dump packet, the bounded bitmap/cpumask starter packet, the bounded list/hlist starter-plus-dump packet, the focused policy slice, the directly readable shared validator entrypoint, the bounded catalog helper, the shared ABI manifest, the separately landed linux-header governance note, or the adjacent export/UAPI layout replay pair as evidence that the broader Phase 3 ABI substrate, export/UAPI header-family survey packet, IDR/IDA family, or shared replay routes already ship on `master`.

## Same-family follow-through present on `master`

Current `master` also directly serves the focused `Documentation/zigux/phase3-abi-h-boundary-next-step.md` note as the packet-local `include/zigux/abi.h` companion beside the dedicated `Documentation/zigux/phase3-abi-header-family-survey.md` plus `scripts/zigux/validate-phase3-abi-header-family-survey.py` follow-through and `Documentation/zigux/phase3-linux-zigux-header-governance.md`, but those returned same-family surfaces should not be used here to imply that the broader shared Phase 3 replay packet has returned.

Current `master` does still ship the separately readable shared validator entrypoint through `scripts/zigux/validate-phase3.py` together with the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, and it also directly serves `scripts/zigux/phase3_catalog.py` together with `zigux/tests/fixtures/phase3_abi_manifest.json`, but those shared validation, catalog, and manifest surfaces should not be used here to imply that the broader validator-support or shared replay packet has returned beyond that bounded survey-plus-next-step companion packet already enumerated here.

Current `master` also keeps this note's dedicated packet-local validator explicit through `scripts/zigux/validate-phase3-validator-support-surface.py`, and that validator should stay aligned with this note rather than being left implicit behind the broader shared `scripts/zigux/validate-phase3.py` entrypoint.

Current `master` does still ship the adjacent low-level-wrapper packet through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/helpers/unsafe_policy.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, and it separately ships the adjacent export/UAPI layout replay pair through `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig`, but those separate wrapper and replay surfaces should not be used here to imply that the broader validator-support or export/UAPI survey packet has returned.

That adjacent low-level-wrapper packet now keeps `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `make -C zigux phase3-low-level-wrappers-test` directly readable on current `master`, but those returned wrapper-local surfaces should stay adjacent here instead of being promoted into broader validator support.

## Shared reminder follow-up

`Documentation/zigux/README.md` now keeps the validator-support, `err_ptr` / `xarray`, bitmap/cpumask, list/hlist, `xarray_slot`, shared catalog companion, and bounded export/UAPI plus header-family reminder surfaces explicit beside the starter, policy, low-level-wrapper, and layout-replay packet, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.

`zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.

`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root, review-checklist, tests-root, and scripts-root summaries, keeps the returned header-family survey follow-through explicit as a same-family companion, and records that no same-lane shared-summary drift remains on current `master`.

`scripts/zigux/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the shared ABI manifest companion, export/UAPI layout replay pair, named Linux-side boundary-header helper family, and direct C smoke proof, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.

Keep any same-lane follow-up parked unless current `master` changes again and reopens a smaller one-file shared-summary or scripts-root inventory drift. This note should not be used to imply that the broader Phase 3 ABI substrate, export/UAPI survey packet, catalog wiring, IDR/IDA family, or shared replay routes have returned.

## Scope

This note is limited to the current validator-support posture for Phase 3. It keeps the directly readable starter packet, the machine-readable manifests, the direct compile replay, the starter export shim companion, the helper-local fixture-backed parity packet, the helper-local `xarray_slot` starter-plus-dump packet, the helper-local `idr_slot` starter-plus-dump packet, the bounded bitmap/cpumask and list/hlist starter-plus-dump packets, the focused policy slice, the dedicated packet-local validator, the separately readable shared validator entrypoint and shared ABI checker, the bounded catalog helper, the shared ABI manifest, the separately landed linux-header governance note, the separately landed header-family survey follow-through, the focused abi.h next-step companion, the adjacent low-level-wrapper packet including its directly coupled `unsafe_policy` and `narrow` surfaces, and the adjacent export/UAPI layout replay pair explicit; marks any broader shared replay routes as current gaps; records the separately landed linux-header governance note without promoting it into broader validator support; records the separately landed header-family survey follow-through without promoting it into broader validator support; records the focused abi.h next-step companion without promoting it into broader validator support; records the separately landed low-level-wrapper packet without promoting it into broader validator support; and records the aligned docs-root, review-checklist, tests-root, and scripts-root summaries together with the closed shared-summary drift while keeping any future scripts-root inventory follow-through separate. This note does not claim that the broader Phase 3 ABI substrate, IDR/IDA family, or shared replay routes have returned.
