# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reread against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=no-missing-shared-abi-or-binding-scaffold-on-current-master-the-remaining-gap-is-keeping-the-manifest-backed-64-file-phase-3-packet-the-shared-abi-slice-the-dedicated-bindings-governance-note-the-lane-owner-map-the-header-family-reminders-the-validator-support-note-and-the-direct-phase3_abi-replay-aligned-now-that-the-starter-dev_t-plus-notifier-binding-trio-and-focused-low-level-wrapper-anchors-all-ship-together`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=the bounded ABI lane still routes through Documentation/zigux/phase3-bindings-governance.md, Documentation/zigux/phase3-abi-bindings-survey.md, Documentation/zigux/phase3-boundary-lane-sequencing.md, Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-kernel-export-shim-governance.md, Documentation/zigux/phase3-policy-unsafe-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, scripts/zigux/validate-phase3-linux-zigux-header-governance.py, Documentation/zigux/phase3-abi-h-boundary-next-step.md, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, Documentation/zigux/phase3-validator-support-surface.md, include/zigux/dev_t.h, zigux/bindings/dev_t.zig, zigux/bindings/notifier_abi.zig, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/validate-phase3.py, scripts/zigux/validate-phase3-validator-support-surface.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/validate-phase3-export-uapi-survey.py, scripts/zigux/validate-phase3-policy-unsafe-survey.py, scripts/zigux/check-phase3-policy-byte-guards.py, scripts/zigux/check-phase3-policy-unsafe-focused-replay.py, scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py, scripts/zigux/survey-phase3-abi-constant-parity.py, scripts/zigux/validate-phase3-abi-header-family-survey.py, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, the manifest-backed file inventory, zigux/tests/phase3_abi.zig, zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c, zigux/tests/fixtures/phase3_abi/expected.json, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, and the live public zigux/uapi tree, so the current requirement is keeping the manifest-backed inventory, the direct phase3_abi replay plus its committed fixture pair, the dedicated bindings-governance note, the dedicated ABI-and-bindings survey, the dedicated policy-and-unsafe boundary survey, the dedicated boundary-lane owner map, the dedicated include/linux/zigux.h governance validator, the surviving dump gate, the coupled panic, allocator, atomic, barrier, MMIO, and narrow-unsafe helper packet, the coupled policy-and-unsafe validators, the focused low-level-wrapper replay and build anchor, the starter-UAPI packet, and reminder-surface markers aligned now that scripts/zigux/validate-phase3.py already exact-requires include/zigux/dev_t.h, zigux/bindings/dev_t.zig, and zigux/bindings/notifier_abi.zig beside the shared packet`
- `PHASE3_NEXT_SAFE_STEP=before widening any starter-UAPI companion, bindings-governance note, ABI-and-bindings survey, policy-and-unsafe survey, boundary-lane owner map, kernel-export governance note, header-family reminder, header-governance note, direct phase3_abi replay anchor, coupled panic/allocator/atomic/barrier/mmio helper, coupled policy-and-unsafe validator, or low-level-wrapper replay/build anchor, keep this lane limited to the next one-file shared-abi-slice-manifest-survey-or-governance truthfulness repair that preserves the current manifest-backed 64-file packet and direct phase3_abi replay alignment`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Packet Markers

- `Documentation/zigux/phase3-bindings-governance.md`
- `Documentation/zigux/phase3-abi-bindings-survey.md`
- `Documentation/zigux/phase3-boundary-lane-sequencing.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/check-phase3-policy-byte-guards.py`
- `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`
- `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`
- `scripts/zigux/validate-phase3-linux-zigux-header-governance.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `python3 scripts/zigux/check-phase3-abi.py --self-test`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`

## Current Gap

The Phase 3 roadmap still requires a narrow and explicit export shim plus starter UAPI boundary. On the current inspected `master`, the same-lane shared ABI reminder gap is no longer missing scaffold in the tree or in the broad validator inventory: the live manifest-backed packet already ships `include/zigux/dev_t.h`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/notifier_abi.zig`, and `scripts/zigux/validate-phase3.py` already exact-requires that trio beside the direct `phase3_abi` replay, the shared ABI header, the starter UAPI pair, and the adjacent validator-support, policy-and-unsafe, export-UAPI, and low-level-wrapper reminder packet. The remaining same-lane job is keeping the shared ABI slice, the manifest-backed inventory, the dedicated bindings-governance note, the lane-owner map, the header-family reminders, the validator-support note, and the direct `phase3_abi` replay aligned so the current packet can be reread from repo evidence without reconstructing it from neighboring notes.

- current `master` already ships `Documentation/zigux/phase3-bindings-governance.md`, `Documentation/zigux/phase3-abi-bindings-survey.md`, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/zigux/dev_t.h`, `zigux/bindings/dev_t.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `scripts/zigux/validate-phase3-abi-bindings-syntax.py`, and `scripts/zigux/validate-phase3.py` now exact-requires the same trio beside the broader 64-file shared packet.
- the remaining same-lane rule is to keep the shared ABI slice, the manifest-backed inventory, the dedicated bindings-governance note, the lane-owner map, the header-family reminders, the validator-support note, and the direct replay honest together, and to avoid reverting to older wording that says the broad validator still trails the tree.
- broader Phase 3 completion still depends on the shared ABI slice, the bindings and governance packet, and any future top-level export or UAPI entry points staying explicit instead of treating this reminder-surface repair as whole-phase closure.
- if a future run reopens this packet, keep it inside that exact shared reminder sync and refresh this note plus the touched survey, manifest, or validator-support surface in the same bounded step.

## Scope

This survey stays packet-local to the shipped starter export shim, the starter `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the shared `zigux/tests/fixtures/phase3_abi_manifest.json` inventory marker, the shared `zigux/tests/phase3_abi_dump.zig` dump anchor, and the shared Phase 3 interop, compile, and dump routes that currently exercise them. It does not claim broader header-governance growth, a larger UAPI family, dedicated export/UAPI-only replay files, or deeper runtime ownership beyond the readable starter packet on the current inspected head.
