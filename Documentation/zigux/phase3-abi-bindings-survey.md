# Phase 3 ABI and Bindings Survey

This note records the current shared ABI and bindings review surface that still anchors the bounded Phase 3 interop substrate on live `master`.

## Status

- `PHASE3_ROADMAP_REQUIREMENTS=explicit-export-shims-generated-or-curated-bindings-layout-assertions-explicit-panic-and-allocator-policy-approved-atomic-barrier-and-mmio-wrappers-and-a-narrow-unsafe-surface`
- `PHASE3_LEDGER_BASELINE=feat(zigux): start bounded Phase 3 abi substrate skeleton`
- `PHASE3_SHARED_PACKET_RULE=shared-abi-and-bindings-lane-owns-broad-packet-accounting-layout-entrypoint-truth-and-direct-phase3_abi-replay-alignment`
- `PHASE3_CURRENT_INTEROP_GAP=no-missing-shared-abi-or-binding-scaffold-on-current-master-the-remaining-gap-is-keeping-one-dedicated-shared-survey-aligned-with-the-manifest-abi-slice-and-lane-owner-map`
- `PHASE3_NEXT_SAFE_STEP=keep-this-lane-limited-to-shared-abi-slice-manifest-or-survey-truthfulness-when-abi-h-bindings-layout-assert-or-direct-phase3_abi-replay-surfaces-move`

## Current packet

- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-boundary-lane-sequencing.md`

## Roadmap fit

Phase 3 is where Zigux defines the permanent C/Zigux boundary. The roadmap still requires explicit export shims, curated bindings, layout assertions, explicit panic and allocator policy, approved atomic, barrier, and MMIO wrappers, and a narrow unsafe surface.

Current `master` already ships that substrate as a shared ABI and bindings packet plus the adjacent export-UAPI, policy-unsafe, and low-level-wrapper lanes. For the shared packet itself, the honest gap is no longer missing scaffold in `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/layout_assert.zig`, or the direct `phase3_abi` replay. The remaining same-lane job is keeping the broad reminder surfaces aligned so the roadmap-backed packet can be reread from current repo evidence without reconstructing it from several neighboring notes.

## Review boundary

- the shared ABI and bindings packet owns the broad ABI slice summary, manifest-backed packet accounting, shared header and binding truthfulness, `zigux/helpers/layout_assert.zig` layout-entrypoint truth, and the direct `zigux/tests/phase3_abi.zig` replay surface
- `Documentation/zigux/phase3-kernel-export-shim-governance.md` plus `Documentation/zigux/phase3-export-uapi-boundary-survey.md` still own the starter export-shim and starter-UAPI packet
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` still owns panic-mode, allocator-mode, unsafe-scope, and policy-aware MMIO admission drift
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` still owns direct atomic, barrier, and MMIO behavior drift
- `Documentation/zigux/phase3-validator-support-surface.md` still owns shared validator-entrypoint, catalog, wrapper-generation, README, and make-route truthfulness

## Current gap

No missing roadmap-backed ABI or bindings starter surface is visible on current `master`: `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/layout_assert.zig`, the direct `phase3_abi` replay, the fixture pair, and the manifest-backed inventory already ship.

The reviewability gap was narrower than a missing helper or binding. Before this note, the shared packet had to be inferred indirectly from `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, and `zigux/tests/fixtures/phase3_abi_manifest.json` together. Adding a dedicated ABI-and-bindings survey closes that bounded repo-reality gap and makes the shared interop packet explicit without reopening the adjacent export-UAPI, policy-unsafe, low-level-wrapper, or validator-support lanes.

## Shared reminder

Broad Phase 3 summaries that name the shared ABI and bindings packet should keep this survey explicit beside `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/layout_assert.zig`, `zigux/tests/phase3_abi.zig`, `scripts/zigux/check-phase3-abi.py`, and `scripts/zigux/survey-phase3-abi-constant-parity.py`. Future reopening should stay inside that same shared packet and adjust the survey, manifest-backed inventory, or broad ABI summary together only when a real shared ABI or bindings surface moves.
