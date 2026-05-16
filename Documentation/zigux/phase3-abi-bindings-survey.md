# Phase 3 ABI and Bindings Survey

This note records the current shared ABI and bindings review surface that still anchors the bounded Phase 3 interop substrate on live `master`.

## Status

- `PHASE3_ROADMAP_REQUIREMENTS=explicit-export-shims-generated-or-curated-bindings-layout-assertions-explicit-panic-and-allocator-policy-approved-atomic-barrier-and-mmio-wrappers-and-a-narrow-unsafe-surface`
- `PHASE3_LEDGER_BASELINE=feat(zigux): start bounded Phase 3 abi substrate skeleton`
- `PHASE3_SHARED_PACKET_RULE=shared-abi-and-bindings-lane-owns-broad-packet-accounting-layout-entrypoint-truth-and-direct-phase3_abi-replay-alignment`
- `PHASE3_CURRENT_INTEROP_GAP=no-missing-shared-abi-or-binding-scaffold-on-current-master-the-remaining-gap-is-scripts-root-reminder-surface-drift-because-Documentation/zigux/README.md-Documentation/zigux/phase3-abi-slice.md-and-zigux/tests/README.md-now-keep-the-dedicated-abi-and-bindings-survey-plus-bindings-governance-note-explicit-while-scripts/zigux/README.md-still-under-counts-that-dedicated-survey-packet-even-though-the-manifest-backed-66-file-shared-packet-the-lane-owner-map-the-header-family-reminders-the-validator-support-note-and-the-direct-phase3_abi-replay-still-ship-together`
- `PHASE3_NEXT_SAFE_STEP=keep-this-lane-limited-to-this-survey-plus-the-next-one-file-follow-through-in-scripts/zigux/README.md-so-the-dedicated-abi-and-bindings-survey-plus-bindings-governance-note-are-explicit-across-the-broad-reminder-surfaces-again`

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
- `Documentation/zigux/phase3-abi-bindings-survey.md`
- `Documentation/zigux/phase3-bindings-governance.md`
- `Documentation/zigux/phase3-boundary-lane-sequencing.md`

Live `master` now routes that core list through a broader 66-file manifest-backed reminder packet. The same inventory also keeps `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `zigux/uapi/dev_t.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` explicit beside this survey so the shared ABI packet can be reread from one manifest-backed packet without pretending this lane owns those neighboring export-UAPI, kernel-export, Linux-facing header-governance, low-level-wrapper implementation, or broader reminder-summary surfaces.

## Roadmap fit

Phase 3 is where Zigux defines the permanent C/Zigux boundary. The roadmap still requires explicit export shims, curated bindings, layout assertions, explicit panic and allocator policy, approved atomic, barrier, and MMIO wrappers, and a narrow unsafe surface.

Current `master` already ships that substrate as a shared ABI and bindings packet plus the adjacent export-UAPI, policy-unsafe, low-level-wrapper, header-family, and validator-support lanes. For the shared packet itself, the honest gap is no longer missing scaffold in `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/layout_assert.zig`, or the direct `phase3_abi` replay. The current same-lane drift is narrower scripts-root reminder-surface truthfulness: `Documentation/zigux/README.md`, `Documentation/zigux/phase3-abi-slice.md`, and `zigux/tests/README.md` already keep this survey plus `Documentation/zigux/phase3-bindings-governance.md` explicit, while `scripts/zigux/README.md` still under-counts that dedicated survey packet and forces reviewers to reconstruct it from neighboring notes.

## Review boundary

- the shared ABI and bindings packet owns the broad ABI slice summary, manifest-backed packet accounting, shared header and binding truthfulness, `zigux/helpers/layout_assert.zig` layout-entrypoint truth, the direct `zigux/tests/phase3_abi.zig` replay surface, and the dedicated `Documentation/zigux/phase3-bindings-governance.md` reminder for the curated bindings trio
- `Documentation/zigux/phase3-kernel-export-shim-governance.md` plus `Documentation/zigux/phase3-export-uapi-boundary-survey.md` still own the starter export-shim and starter-UAPI packet
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` still owns panic-mode, allocator-mode, unsafe-scope, and policy-aware MMIO admission drift
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` still owns direct atomic, barrier, and MMIO behavior drift
- `Documentation/zigux/phase3-validator-support-surface.md` still owns shared validator-entrypoint, catalog, wrapper-generation, README, and make-route truthfulness

## Current gap

No missing roadmap-backed ABI or bindings starter surface is visible on current `master`: `include/zigux/abi.h`, `include/zigux/dev_t.h`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/layout_assert.zig`, the direct `phase3_abi` replay, the fixture pair, and the manifest-backed inventory already ship.

Adding a dedicated ABI-and-bindings survey closed the broader repo-reality gap, and the current reread now shows `Documentation/zigux/phase3-abi-slice.md` and `zigux/tests/README.md` are aligned with that follow-through. The remaining same-lane job is narrower scripts-root reminder-surface truthfulness: `Documentation/zigux/README.md`, `Documentation/zigux/phase3-abi-slice.md`, and `zigux/tests/README.md` keep both this survey and `Documentation/zigux/phase3-bindings-governance.md` explicit, while `scripts/zigux/README.md` still under-counts the dedicated ABI-and-bindings survey packet. Keep that survey, the manifest-backed inventory, the docs-root, scripts-root, and tests-root reminder surfaces, the shared ABI slice, the dedicated bindings-governance note, the lane-owner map, the header-family reminders, and the validator-support note aligned so the bindings trio, starter `dev_t` companion, adjacent export-UAPI and kernel-export reminder surfaces, the Linux-facing header-governance note, the broader reminder summaries, and the low-level-wrapper reminder anchors stay reviewable without reopening the neighboring export-UAPI, kernel-export, Linux-facing header-governance, policy-unsafe, low-level-wrapper, or validator-support implementation lanes.

## Shared reminder

Broad Phase 3 summaries that name the shared ABI and bindings packet should keep this survey explicit beside `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-bindings-governance.md`, `Documentation/zigux/phase3-boundary-lane-sequencing.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, `include/zigux/abi.h`, `include/zigux/dev_t.h`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/layout_assert.zig`, `zigux/uapi/dev_t.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/check-phase3-abi-dump-gate.py`, `scripts/zigux/validate-phase3-abi-bindings-syntax.py`, and `scripts/zigux/survey-phase3-abi-constant-parity.py`. On the current inspected `master`, `Documentation/zigux/README.md`, `Documentation/zigux/phase3-abi-slice.md`, and `zigux/tests/README.md` already do this; the next bounded same-lane follow-through is to refresh `scripts/zigux/README.md` without widening into owner-map, export-UAPI, policy-unsafe, low-level-wrapper, or validator-support implementation work.
