# Phase 11 Shared Replay Contract

This note records the current shared contributor replay surface for the shipped Phase 11 simple-driver packet.

## Status

- `PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable`
- scope: keep the current watchdog and `hvc_console` starter tranche reviewable through one shared replay route while teardown and failure-mode parity stay explicit and host-backed integration remains out of scope

## Current Shared Review Surface On `master`

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/Makefile`

## Shared Replay Commands

- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

Inside that shared `phase11_build.zig` route, `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff, missing-reference failure mode, and teardown-gating replay explicit without implying live tty teardown or host-backed cleanup.

The dedicated archival HVC survey replay stays separate:

- `zigux/tests/phase11_hvc_console_survey.zig`

## What This Contract Does Not Claim

- there is no dedicated shared `validate-phase11.py` on `master`
- there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`
- there is no broader shared checker-script packet on `master`
- this contract does not claim tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, PM base plumbing, poweroff-handler coordination, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 follow-through should stay inside the next smallest hardware-validation matrix, focused replay, teardown-parity note, failure-mode note, or shared reviewability step until broader validator assets actually land.
