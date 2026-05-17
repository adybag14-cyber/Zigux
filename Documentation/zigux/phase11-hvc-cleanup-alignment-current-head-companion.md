# Phase 11 HVC Cleanup Alignment Current-Head Companion

This note records the bounded current-head readback for the Phase 11 HVC cleanup-alignment packet.

## Status

- `PHASE11_STATUS=current_head_companion_landed`
- `PHASE11_FAMILY=hvc-console-cleanup-alignment`
- `PHASE11_SURFACE=checker-truthfulness-readback`
- `PHASE11_PROVENANCE_MODE=dated_master_readback`
- surveyed against current `master` readback on `2026-05-17`
- scope: keep the current HVC cleanup-alignment reminder truthful without widening into notifier callback execution, khvcd execution, tty registration, sysrq execution, watchdog-core glue, or host-backed teardown
- role: current-head truthfulness companion for the bounded Phase 11 HVC continuity packet while the returned direct HVC starter-depth packet stays explicit beside the smaller proof-backed packet

## Why this companion exists

The Phase 11 roadmap still keeps simple-driver progress inside bounded teardown and failure-mode review surfaces before riskier integration work.

The smallest honest same-lane follow-up in this environment is therefore not to recreate older HVC packet wording from memory, but to keep one current-head companion aligned with what current `master` now materializes again through the direct HVC starter packet, the cleanup proof shards, and the helper-boundary notes.

## Current Repo Reality

Current `master` keeps the bounded HVC continuity packet reviewable through these live surfaces:

- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Current `master` also keeps the returned direct HVC starter-depth packet explicit through these live surfaces:

- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`

An earlier narrower rerun in this family had recorded those direct file paths as temporarily absent from one readback path. The coupled HVC survey packet and checker-backed continuity surfaces now reread those paths directly again, so that older missing-readback wording is superseded run history rather than current repo truth.

## Drift Kept Explicit

Current `master` keeps both the smaller proof-backed HVC continuity packet and the returned direct HVC driver, helper, replay, teardown, validation-matrix, and survey-checker packet reviewable together.

This companion therefore exists to keep that combined current-head packet explicit so nearby shared reminders do not understate the direct HVC starter-depth surfaces after they have returned to current readback.

## Safe Reading

Use the current HVC survey note, this companion, the verify-helper-boundary note, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, the shared build inventory anchor, the surviving HVC proof shards, and the returned direct HVC starter-depth packet as the truthful readback for this lane on current `master`.

Treat any older missing-readback wording in this companion as superseded run history rather than as the current boundary of the HVC packet.

## Boundary Kept Honest

This companion does not claim:

- notifier callback execution
- khvcd worker execution
- tty-driver registration
- live sysrq dispatch
- host-backed teardown or transport parity

It only records that current `master` again keeps both the smaller proof-backed continuity packet and the direct HVC starter-depth packet reviewable together.

## Next bounded step

If a future reread drops any direct HVC starter, replay, teardown, validation-matrix, or survey-checker path again, refresh this companion, the HVC survey note, and any coupled checker in one pass.

Until then, keep both the smaller inventory-backed continuity packet and the returned direct HVC starter-depth packet explicit across the broad Phase 11 reminder surfaces.
