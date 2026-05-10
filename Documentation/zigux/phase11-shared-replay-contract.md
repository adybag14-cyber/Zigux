# Phase 11 Shared Replay Contract

This note records the current shared contributor replay surface for the shipped Phase 11 simple-driver packet.

## Status

- `PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable`
- scope: keep the current watchdog, shared header parity, and `hvc_console` starter tranche reviewable through one shared replay route while teardown and failure-mode parity stay explicit, the shared closure checkpoint stays recorded, and host-backed integration remains out of scope

## Current Shared Review Surface On `master`

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_hvc_console.zig`
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
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`

The shipped gpio watchdog sub-packet inside that shared route stays explicit as `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`.

The focused gpio platform-drvdata checkpoint also stays explicit beside that shared route as `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, with `Documentation/zigux/phase11-gpio-wdt-module-slice.md` recording why that early `platform_set_drvdata()` ordering replay remains dedicated local evidence instead of shared-build green status today.

The shipped bcm2835 watchdog sub-packet inside that shared route stays explicit as `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`.

The shipped DesignWare watchdog sub-packet inside that shared route stays explicit as `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`.

The shipped HVC starter sub-packet inside that shared route stays explicit as `phase11-hvc-console-tests`, `phase11-hvc-console-verify-tests`, and `phase11-hvc-cleanup-tests`, while the dedicated archival survey remains `phase11-hvc-console-survey-tests`.

The active watchdog validation packets also stay explicit beside that shared route:

- gpio watchdog: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, and the focused local `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` checkpoint
- bcm2835 watchdog: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`
- DesignWare watchdog: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and the shared `phase11-dw-wdt-registration-scaffold-tests` plus `phase11-dw-wdt-verify-tests` replay artifacts

The dedicated archival bcm2835 evidence also stays explicit beside that shared route:

- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`

The dedicated archival DesignWare evidence also stays explicit beside that shared route:

- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-dw-wdt-packet.py`

The parked driver-lane ownership map also stays explicit beside that replay route:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`

The shared closure checkpoint now also stays explicit beside that replay route:

- `Documentation/zigux/phase11-closure-note.md`

The dedicated archival HVC evidence still stays explicit beside that shared route:

- `Documentation/zigux/phase11-hvc-console-slice.md`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `make -C zigux phase11-hvc-survey`

`Documentation/zigux/phase11-hvc-console-slice.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `Documentation/zigux/phase11-hvc-console-survey.md`, and `Documentation/zigux/phase11-hvc-console-validation-matrix.md` keep the archival HVC landing checkpoint named alongside the survey note and validation matrix so the dedicated HVC packet does not blur back into the shared replay route.

`Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps the close, cleanup, remove, write-to-hangup, and hangup-disconnect ownership split explicit in one driver-local note.

Repo reality now carries one bounded starter and validation matrix for each Phase 11 simple-production-driver roadmap anchor at starter depth:

- `drivers/watchdog/gpio_wdt.zig`
- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/tty/hvc/hvc_console.zig`

That means the remaining Phase 11 gap is live integration depth, not missing starter coverage.

The focused shared header-boundary evidence also stays explicit beside that shared route:

- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

`Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all keep the older docs-root reread, the dedicated gpio teardown companion, the dedicated DesignWare packet-checker route, the dedicated DesignWare teardown companion, and the dedicated HVC survey packet explicit beside the parked driver-lane owner map on current `master`. Reopen `Documentation/zigux/review-checklist.md` next; its broad Phase 11 checklist question still names the shared contract, the parked shared closure checkpoint, the focused header-boundary packet, and the dedicated HVC survey route, but it does not yet keep the dedicated bcm2835 and DesignWare archival checker routes explicit even though the shared contract, scripts root, and tests root now do.

## What This Contract Does Not Claim

- there is no shared `make -C zigux phase11-validate` target on `master`
- there is no dedicated shared `validate-phase11.py` on `master`
- there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`
- beyond `scripts/zigux/check-phase11-shared-replay-contract.py`, the dedicated `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` route, the dedicated `scripts/zigux/check-phase11-dw-wdt-packet.py` route, the focused `scripts/zigux/check-phase11-header-boundary-packet.py` route, and the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` route, there is no broader multi-checker Phase 11 validator stack on `master`
- this contract does not claim tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, PM base plumbing, poweroff-handler coordination, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 follow-through should stay inside the next smallest hardware-validation matrix, focused replay, teardown-parity note, failure-mode note, registration-facing handoff note, driver-lane sequencing sync, shared closure-note sync, or shared review-surface sync across the gpio, bcm2835, dw, header-boundary, and HVC packet rather than widening into new driver behavior or broader validator assets before those files actually land.
