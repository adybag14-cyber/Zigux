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
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Shared Replay Commands

- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

Inside that shared `phase11_build.zig` route, the watchdog, shared header-parity, and HVC starter replays stay bundled together:

- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`

The active watchdog validation packets also stay explicit beside that shared route:

- gpio watchdog: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`
- bcm2835 watchdog: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`
- DesignWare watchdog: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `drivers/watchdog/dw_wdt_verify.zig`

The parked driver-lane ownership map also stays explicit beside that replay route:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`

The dedicated archival HVC evidence still stays explicit beside that shared route:

- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `make -C zigux phase11-hvc-survey`

The focused shared header-boundary evidence also stays explicit beside that shared route:

- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

`Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` keep that same shared-versus-dedicated replay split explicit, while `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff, missing-reference failure mode, and teardown-gating replay reviewable without implying live tty teardown or host-backed cleanup, `drivers/tty/hvc/hvc_console_verify.zig` keeps one compile-local final-close and hung-up or detached teardown replay beside the shared packet, `Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps the close, cleanup, and remove ownership split explicit in one driver-local note, and `zigux/tests/phase11_hvc_console_manifest.json` keeps the archival HVC landing checkpoint named alongside the survey note and validation matrix.

## What This Contract Does Not Claim

- there is no shared `make -C zigux phase11-validate` target on `master`
- there is no dedicated shared `validate-phase11.py` on `master`
- there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`
- beyond `scripts/zigux/check-phase11-shared-replay-contract.py`, the focused `scripts/zigux/check-phase11-header-boundary-packet.py` route, and the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` route, there is no broader multi-checker Phase 11 validator stack on `master`
- this contract does not claim tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, PM base plumbing, poweroff-handler coordination, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 follow-through should stay inside the next smallest hardware-validation matrix, focused replay, teardown-parity note, failure-mode note, registration-facing handoff note, driver-lane sequencing sync, or shared review-surface sync across the gpio, bcm2835, dw, header-boundary, and HVC packet rather than widening into new driver behavior or broader validator assets before those files actually land.
