# Phase 3 Release Closure Checklist

This checklist is the tranche-closure planning companion for the current Phase 3 packet.

It is a PMO release artifact only. It does not claim that Phase 3 is already closed, and it does not create a new replay route.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- roadmap anchor: Phase 3 ABI and interop substrate
- bootstrap-ledger anchor: start with the ABI substrate skeleton, then the bitmap/cpumask, list/hlist, and err_ptr/xarray interop slices before broader runtime ambitions
- shared ABI slice companion: `Documentation/zigux/phase3-abi-slice.md`
- shared policy companion: `Documentation/zigux/phase3-policy-slice.md`
- shared validator-support companion: `Documentation/zigux/phase3-validator-support-surface.md`
- shared reminder companion: `Documentation/zigux/phase3-shared-reminder-gap.md`
- export and header companions: `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, and `Documentation/zigux/phase3-abi-header-family-survey.md`
- low-level wrapper companion: `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- focused interop companions: `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `Documentation/zigux/phase3-list-hlist-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, and `Documentation/zigux/phase3-xarray-slot-slice.md`
- current authority: the shared ABI slice note, the bounded interop slice notes, the policy and low-level-wrapper notes, the shared manifest-backed validators, the directly readable starter-packet and replay routes, and the docs-root reminder packet remain the trustworthy current-master sources for this tranche

## Closure Gates

Keep Phase 3 marked open until every item below is true on current `master`:

- The docs-root release packet stays aligned across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, this checklist, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-shared-reminder-gap.md`, and `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`.
- The bounded interop packet stays explicit rather than implied: `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `Documentation/zigux/phase3-list-hlist-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, and `Documentation/zigux/phase3-xarray-slot-slice.md` keep the current helper-local ABI evidence reviewable without being rounded up into full Phase 3 completion.
- The shared validator packet still reruns through `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3-validator-support-surface.py`, `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`, `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`, `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`, and `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`.
- The shared support bundle still reruns through `python3 scripts/zigux/check-phase3-abi.py`, `python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test`, `python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test`, `python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test`, `python3 scripts/zigux/check-phase3-selftest-surface.py --self-test`, `python3 scripts/zigux/check-phase3-catalog-selftest.py`, `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`, and `python3 scripts/zigux/check-phase3-policy-dump.py --self-test`.
- The shared manifest-backed ABI inventory remains explicit through `zigux/tests/fixtures/phase3_abi_manifest.json`, `scripts/zigux/phase3_catalog.py`, `scripts/zigux/run-phase3-checks.py`, and `scripts/zigux/validate_phase3_selftest.py`.
- The directly readable replay routes remain explicit through `zig build phase3-abi-core-packet --build-file zigux/tests/build.zig`, `zig build phase3-dump --build-file zigux/tests/build.zig`, `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`, and `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`.
- The directly readable Makefile-backed replay routes remain bounded and truthful through `make -C zigux phase3-export-uapi-layout-test`, `make -C zigux phase3-low-level-wrappers`, and `make -C zigux phase3-low-level-wrappers-test`; keep these as explicit route evidence, not as proof that the whole Phase 3 tranche is closed.
- The shared packet stays limited to bounded ABI, export/UAPI, header-family, policy, unsafe-boundary, and low-level-wrapper evidence rather than deeper scheduler, allocator, MMIO-heavy driver, DMA, or runtime-core completion claims.

## Current Open Blockers

Keep the checklist in the open state while these Phase 3 closure blockers remain true:

- Phase 3 is broader on current `master` than the original bootstrap ledger slices, but it is still a bounded collection of starter packets, focused surveys, and validator-backed replay routes rather than a closed substrate tranche.
- The shared docs root has slice and survey coverage, but before this note it did not have a dedicated release-closure artifact that gathered the Phase 3 packet into one explicit PMO gate.
- The bounded interop families remain separate review surfaces. `bitmap/cpumask`, `list/hlist`, `err_ptr/xarray`, and `xarray_slot` are directly readable on current `master`, but they are still helper-local slice evidence rather than a full merged closure signal.
- The export/UAPI and policy packet remains partial by design. `include/linux/zigux.h`, `include/zigux/abi.h`, `include/zigux/dev_t.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, and `zigux/unsafe/narrow.zig` are real current-master evidence, but they do not by themselves close the larger Phase 3 boundary.
- The low-level-wrapper note must stay below runtime-heavy claims. The returned wrapper routes and helper packet are useful validation evidence, but they are not permission to imply broader Phase 4, Phase 9, or driver-delivery readiness.

## Degraded Validation Path

If a full local repo checkout or broader build path is unavailable, keep the same validation order and start with the Python truthfulness packet before relying on focused Zig replay routes:

1. `python3 scripts/zigux/validate-phase3.py`
2. `python3 scripts/zigux/validate-phase3-validator-support-surface.py`
3. `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
4. `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
5. `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`
6. `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
7. `python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test`
8. `python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test`
9. `python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test`
10. `python3 scripts/zigux/check-phase3-selftest-surface.py --self-test`
11. `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
12. `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`
13. `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

Do not invent a broader closure route, a new aggregate Phase 3 Makefile wrapper, or a deeper runtime replay path while using the degraded route.

## Re-Read Before Changing Closure State

Before changing this checklist from open to closed, reread these files together:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `Documentation/zigux/phase3-list-hlist-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-shared-reminder-gap.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Next Bounded Step

The next honest same-lane follow-through is to add one compact Phase 3 release-sequencing or coordination companion only if a fresh repo-first reread proves the shared packet is drifting across the docs root, scripts-root reminders, or tests-root reminders.

If the shared packet stays aligned, leave this checklist parked and keep helper-local or validator-local follow-through in their dedicated lanes rather than widening this PMO note into implementation claims.

## Non-Goals

- This checklist does not close the Phase 3 tranche by itself.
- This checklist does not widen Phase 3 into new helper, driver, or runtime implementation work.
- This checklist does not change the freeze-map posture.
- This checklist does not promote bounded interop slices into proof that deeper runtime-core delivery is ready.
