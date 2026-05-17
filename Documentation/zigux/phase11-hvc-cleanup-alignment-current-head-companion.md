# Phase 11 HVC Cleanup Alignment Current-Head Companion

This note records the bounded current-head readback for the Phase 11 HVC cleanup-alignment packet.

## Status

- `PHASE11_STATUS=current_head_companion_landed`
- `PHASE11_FAMILY=hvc-console-cleanup-alignment`
- `PHASE11_SURFACE=checker-truthfulness-readback`
- `PHASE11_PROVENANCE_MODE=dated_master_readback`
- surveyed against current `master` readback on `2026-05-17`
- scope: keep the current HVC cleanup-alignment reminder truthful without widening into notifier callback execution, khvcd execution, tty registration, sysrq execution, watchdog-core glue, or host-backed teardown
- role: current-head truthfulness companion for the bounded Phase 11 HVC continuity packet while the broader archival driver and replay surfaces remain absent from direct readback in this lane

## Why this companion exists

The Phase 11 roadmap still keeps simple-driver progress inside bounded teardown and failure-mode review surfaces before riskier integration work.

The smallest honest same-lane follow-up in this environment is therefore not to recreate the older direct HVC packet from historical wording, but to keep one current-head companion aligned with what current `master` actually materializes.

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

Current direct contents reads in this run did not rematerialize:

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

Keep those paths framed as archival packet vocabulary rather than current-head direct-readback evidence until a future reread proves they returned.

## Drift Kept Explicit

Current `master` still keeps the smaller HVC continuity packet above reviewable, while the broader archival HVC driver, helper, replay, teardown, validation-matrix, and survey-checker surfaces remain absent from direct readback.

This companion therefore exists to keep that smaller current-head packet explicit so nearby shared reminders do not re-promote the missing direct HVC files from older wording alone.

## Safe Reading

Use the current HVC survey note, this companion, the verify-helper-boundary note, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, the shared build inventory anchor, and the surviving HVC proof shards as the truthful readback for this lane on current `master`.

Read the archived direct driver, helper, replay, teardown, validation-matrix, and survey-checker paths above as historical packet vocabulary only until a future reread confirms they materialize again.

## Boundary Kept Honest

This companion does not claim:

- that the archived direct HVC driver, verify, sysrq, split-replay, teardown, validation-matrix, or survey-checker packet is back on current `master`
- notifier callback execution
- khvcd worker execution
- tty-driver registration
- live sysrq dispatch
- host-backed teardown or transport parity

It only records the smaller current-head HVC continuity packet that current direct readback still supports.

## Next bounded step

If future direct rereads rematerialize the archived HVC packet, refresh this companion, the HVC survey note, and any coupled checker in one pass.

Until then, keep this smaller inventory-backed continuity packet explicit across the broad Phase 11 reminder surfaces.