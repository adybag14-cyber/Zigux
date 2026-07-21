# Phase 3 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 3 ABI and interop packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_RELEASE_CLOSED=no`
- shared-summary lane owner: `pmo-release`
- scope: keep the active Phase 3 packet reviewable through the current shared ABI, starter-packet, helper-local, export/UAPI, and low-level-wrapper surfaces without implying broader closure or a returned wider validator family
- sequencing companion: `Documentation/zigux/phase3-boundary-lane-sequencing.md`
- ABI slice companion: `Documentation/zigux/phase3-abi-slice.md`
- err_ptr and xarray companion: `Documentation/zigux/phase3-errptr-xarray-slice.md`
- policy companion: `Documentation/zigux/phase3-policy-slice.md`
- validator-support companion: `Documentation/zigux/phase3-validator-support-surface.md`
- export/UAPI companion: `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- low-level-wrapper companion: `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- linux-header governance companion: `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- header-family survey companion: `Documentation/zigux/phase3-abi-header-family-survey.md`
- freeze-map companion: `Documentation/zigux/freeze-map.md`
- shared validator packet: `scripts\zigux/validate_phase3.zig`, `scripts\zigux/check_phase3_abi.zig`, `scripts\zigux/check_phase3_selftest_surface.zig`, `scripts\zigux/check_phase3_readme_tooling_inventory.zig`, `scripts\zigux/check_phase3_catalog_selftest.zig`, `scripts/zigux/phase3_catalog.zig`, `scripts\zigux/validate_phase3_export_uapi_survey.zig`, `scripts\zigux/validate_phase3_low_level_wrapper_survey.zig`, and `scripts\zigux/validate_phase3_abi_header_family_survey.zig`
- shared replay wiring: `zigux/tests/build.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zigux/Makefile`

## Active Shared Packet

Keep shared release wording tied to the bounded Phase 3 substrate family already materialized on current `master`:

- shared ABI boundaries:
  - `include/linux/zigux.h`
  - `include/zigux/dev_t.h`
  - `include/zigux/abi.h`
  - `zigux/bindings/dev_t.zig`
  - `zigux/bindings/version.zig`
  - `zigux/bindings/abi.zig`
  - `zigux/bindings/notifier_abi.zig`
  - `zigux/kernel/export_shim.zig`
  - `zigux/uapi/dev_t.zig`
  - `zigux/uapi/version.zig`
- helper-local active packet:
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
- directly readable shared tests and manifest packet:
  - `zigux/tests/phase3_abi.zig`
  - `zigux/tests/phase3_dev_t_starter_packet.zig`
  - `zigux/tests/phase3_dev_t_starter_packet_build.zig`
  - `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
  - `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
  - `zigux/tests/phase3_xarray_slot_starter_packet.zig`
  - `zigux/tests/phase3_policy_starter_packet.zig`
  - `zigux/tests/phase3_policy_starter_packet_build.zig`
  - `zigux/tests/phase3_low_level_wrappers.zig`
  - `zigux/tests/phase3_low_level_wrappers_build.zig`
  - `zigux/tests/phase3_export_uapi_layout.zig`
  - `zigux/tests/phase3_export_uapi_layout_build.zig`
  - `zigux/tests/fixtures/phase3_abi_manifest.json`

Keep that packet framed as bounded ABI, helper, starter, layout-replay, and survey-backed release evidence. Do not round it up into broader Phase 3 closure, full interop completion, or later-phase runtime delivery.

## Owner Split

- PMO / Release Management: keep this matrix, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, `Documentation/zigux/phase3-validator-support-surface.md`, and the docs-root reminder packet aligned around the same active-not-closed posture and the same bounded replay family.
- ABI and export boundary owners: keep `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/fixtures/phase3_abi_manifest.json` grounded in their shipped reviewability surfaces.
- Helper-local owners: keep the `err_ptr` / `xarray`, `xarray_slot`, policy, and low-level-wrapper slices grounded in `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, and their directly readable helper and test companions instead of promoting them into broader shared-release closure evidence.
- Validator and catalog owners: keep `scripts\zigux/validate_phase3.zig`, `scripts\zigux/check_phase3_abi.zig`, `scripts\zigux/check_phase3_selftest_surface.zig`, `scripts\zigux/check_phase3_readme_tooling_inventory.zig`, `scripts\zigux/check_phase3_catalog_selftest.zig`, `scripts/zigux/phase3_catalog.zig`, `scripts\zigux/validate_phase3_export_uapi_survey.zig`, `scripts\zigux/validate_phase3_low_level_wrapper_survey.zig`, and `scripts\zigux/validate_phase3_abi_header_family_survey.zig` explicit as the current shared truthfulness and rerun packet.

## Release Handle

Keep the stable Phase 3 release-planning handle distinct from the helper-local and validator-local write lanes:

1. `Documentation/zigux/phase3-release-coordination-matrix.md`
2. `Documentation/zigux/phase3-boundary-lane-sequencing.md`
3. `Documentation/zigux/phase3-validator-support-surface.md`
4. `scripts\zigux/validate_phase3.zig`
5. `make -C zigux phase3-validate`
6. `make -C zigux phase3`

Keep these focused rerun routes explicit as bounded companions rather than broader closure proof:

1. `zig build phase3-abi-core-packet --build-file zigux/tests/build.zig`
2. `zig build phase3-dump --build-file zigux/tests/build.zig`
3. `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
4. `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
5. `make -C zigux phase3-policy-starter-packet-test`

That keeps the release handle centered on the shared validator-first and bounded replay packet already wired into current `master`, while leaving broader reminder refreshes or helper-local semantics in their own lanes.

## Boundaries

- This matrix does not close the Phase 3 tranche.
- This matrix does not imply that the wider shared ABI validator family has returned beyond the currently readable packet.
- This matrix does not promote helper-local starter, dump, or survey surfaces into a claim that broader Phase 3 interop delivery is complete.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper transport, queueing, and study-only anchors, so this PMO note must not imply delivery against `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`.

## Review Use

When the shared Phase 3 packet moves:

1. reread this matrix beside `Documentation/zigux/phase3-boundary-lane-sequencing.md`, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, and `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
2. rerun `zig run scripts/zigux/check_phase3_selftest_surface.zig -- --self-test`
3. rerun `zig run scripts/zigux/check_phase3_readme_tooling_inventory.zig -- --self-test`
4. rerun `zig run scripts/zigux/check_phase3_abi.zig -- --self-test`
5. keep any broader README, checklist, or tests-root reminder refresh as a separate same-lane step when a fresh repo reread proves drift there

## Next Bounded Step

The next honest PMO follow-through is not another new release artifact. It is a narrow truthfulness reread to see whether the docs-root, scripts-root, and tests-root shared Phase 3 reminders all name this same active-not-closed packet without drifting into broader closure language.
