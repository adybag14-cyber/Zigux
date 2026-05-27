# Phase 3 Closure

This note is the tranche-closure companion for the current Phase 3 ABI and interop packet.

It is a PMO closure record only. It does not claim that Phase 3 is already closed, and it does not widen the bounded Phase 3 packet into deeper runtime-core delivery.

## Status

- `PHASE3_STATUS=parked`
- `PHASE3_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- roadmap anchor: `Phase 3: ABI and Interop Substrate`
- ledger posture: the bootstrap ledger closes through Phase 2, so this note is the release-planning continuation for the live Phase 3 tranche on current `master`
- primary slice companion: `Documentation/zigux/phase3-abi-slice.md`
- validator-support companion: `Documentation/zigux/phase3-validator-support-surface.md`
- policy companion: `Documentation/zigux/phase3-policy-slice.md`
- shared-reminder companion: `Documentation/zigux/phase3-shared-reminder-gap.md`
- export and header companions: `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, and `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- low-level wrapper companion: `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- shared validator entrypoint: `scripts/zigux/validate-phase3.py`
- shared ABI checker: `scripts/zigux/check-phase3-abi.py`
- shared check runner: `scripts/zigux/run-phase3-checks.py`
- shared selftest driver: `scripts/zigux/validate_phase3_selftest.py`
- manifest authority: `zigux/tests/fixtures/phase3_abi_manifest.json`
- shared build wiring: `zigux/tests/build.zig`, `zigux/tests/phase3_export_shim_build.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`

## Release Packet

Keep the current Phase 3 release packet bounded to the directly readable ABI and interop surfaces already on `master`:

- shared ABI starter and reminder packet: `Documentation/zigux/phase3-abi-slice.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `include/zigux/abi.h`, `zigux/uapi/dev_t.zig`, `zigux/uapi/version.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/bindings/header_family.zig`, `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/tests/phase3_export_uapi_c_header_smoke.c`, and `zigux/tests/fixtures/phase3_abi_manifest.json`
- focused helper slices already landed on `master`: `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `Documentation/zigux/phase3-list-hlist-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-xarray-slot-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, and `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- validator and catalog support already landed on `master`: `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-shared-reminder-gap.md`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/check-phase3-abi-support-packet.py`, `scripts/zigux/check-phase3-abi-manifest-replay-routes.py`, `scripts/zigux/check-phase3-shared-tests-routes.py`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/phase3_catalog.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/run-phase3-checks.py`, and `scripts/zigux/validate_phase3_selftest.py`
- policy, export/UAPI, and low-level wrapper surveys already landed on `master`: `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

## Closure Gates

Keep Phase 3 marked open until every item below is true on current `master`:

- the docs-root PMO packet stays aligned across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, this closure note, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-shared-reminder-gap.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- the shared validator entrypoint and replay guards remain directly readable through `scripts/zigux/validate-phase3.py`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/check-phase3-abi-support-packet.py`, `scripts/zigux/check-phase3-abi-manifest-replay-routes.py`, `scripts/zigux/check-phase3-shared-tests-routes.py`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/run-phase3-checks.py`, and `scripts/zigux/validate_phase3_selftest.py`
- the shared ABI manifest and catalog packet remain directly readable through `zigux/tests/fixtures/phase3_abi_manifest.json`, `scripts/zigux/phase3_catalog.py`, and `scripts/zigux/check-phase3-catalog-selftest.py`
- the shared replay and wrapper routes remain visible through `zigux/tests/build.zig`, `zigux/tests/phase3_export_shim_build.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- the bounded helper-slice packet remains explicit through the bitmap/cpumask, list/hlist, err_ptr/xarray, xarray-slot, policy, and low-level-wrapper notes and their directly coupled helper, manifest, and replay surfaces rather than being rounded up into a blanket "Phase 3 complete" claim
- the export and header-family boundary packet remains explicit through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, and the direct export/UAPI layout plus C-header smoke routes instead of being collapsed into a generic ABI-complete claim
- Phase 3 wording stays below broader runtime-core completion, deep-core ownership changes, IDR or IDA expansion, and any claim that the ABI substrate has graduated beyond the current bounded starter, survey, and replay packet

## Current Open Blockers

Keep the closure note in the open state while these same-lane blockers remain true:

- the roadmap-approved Phase 3 packet is still a bounded ABI and interop substrate, not a closed broader runtime-core tranche
- current `master` exposes starter packets, focused helper slices, survey notes, replay routes, and validators, but it does not expose a reviewed Phase 3 closure artifact before this note or a ledger continuation that closes the tranche
- the live packet still depends on separate validator-support, shared-reminder, header-family, export/UAPI, and low-level-wrapper companions rather than a single unified closure gate
- the shared packet still needs to stay honest about bounded helper-family delivery: bitmap/cpumask, list/hlist, err_ptr/xarray, xarray-slot, policy, and low-level-wrapper slices are landed, but that does not close the broader Phase 3 substrate
- deeper Phase 3 follow-through remains outside this PMO packet and must stay in dedicated same-family lanes instead of being implied closed here

## Review Order

When same-lane PMO wording changes, reread in this order:

1. `Documentation/zigux/phase3-abi-slice.md`
2. `Documentation/zigux/phase3-validator-support-surface.md`
3. `Documentation/zigux/phase3-policy-slice.md`
4. `Documentation/zigux/phase3-shared-reminder-gap.md`
5. `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
6. `Documentation/zigux/phase3-abi-header-family-survey.md`
7. `Documentation/zigux/phase3-linux-zigux-header-governance.md`
8. `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
9. `Documentation/zigux/README.md`
10. `scripts/zigux/README.md`
11. `zigux/tests/README.md`
12. `scripts/zigux/validate-phase3.py`
13. `scripts/zigux/check-phase3-abi.py`
14. `zigux/tests/fixtures/phase3_abi_manifest.json`

## Next Bounded Step

The next honest same-lane follow-through is to keep this closure note parked unless one shared reminder surface understates the directly readable Phase 3 packet again. If a PMO refresh is needed later, start with the smallest truthfulness repair in `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or the directly coupled shared reminder note rather than widening into helper-local behavior, validator implementation changes, or new Phase 3 scope claims.

## Non-Goals

- this note does not close Phase 3
- this note does not add a new validator or replay route
- this note does not promote bounded helper slices into blanket runtime-core completion
- this note does not reopen the bootstrap ledger past its reviewed Phase 2 scope
