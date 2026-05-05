# Phase 11 Shared Replay Contract

This note records the current shared contributor replay surface for the shipped Phase 11 simple-driver packet.

## Status

- `PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable`
- scope: keep the current watchdog, shared header parity, and `hvc_console` starter tranche reviewable through one shared replay route while teardown and failure-mode parity stay explicit and host-backed integration remains out of scope

## Current Shared Review Surface On `master`

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `scripts/zigux/validate-phase11.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/Makefile`

## Shared Replay Commands

- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

Inside that shared `phase11_build.zig` route, the watchdog starter and survey replays stay bundled together:

- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`

The paired public-header packet also stays explicit inside that same shared route:

- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`

The HVC-specific packet stays explicit inside that same shared route:

- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`

`scripts/zigux/validate-phase11.py` keeps that same shared simple-driver inventory fail-closed against the shipped replay packet, while `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff, missing-reference failure mode, and teardown-gating replay explicit without implying live tty teardown or host-backed cleanup, and `zigux/tests/phase11_hvc_console_survey.zig` remains the dedicated archival replay for the original HVC roadmap gap.

## What This Contract Does Not Claim

- there is no shared `make -C zigux phase11-validate` target on `master`
- there is no broader multi-checker Phase 11 script packet on `master`
- this contract does not claim tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, PM base plumbing, poweroff-handler coordination, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 follow-through should stay inside the next smallest focused replay, teardown-parity note, failure-mode note, registration-facing handoff note, or shared reviewability sync now that the shipped watchdog, header-boundary, and HVC packet is explicit, and it should avoid broader validator assets until those files actually land.
