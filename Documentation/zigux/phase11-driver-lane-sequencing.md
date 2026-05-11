# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes so shared reminders do not collapse bcm2835, gpio, DesignWare, HVC, and shared header evidence into one noisy bucket.

## Scope

Use this note when a Phase 11 change touches any part of the shipped simple-driver packet under `drivers/watchdog/*.zig`, `drivers/tty/hvc/*.zig`, `Documentation/zigux/phase11-*.md`, `scripts/zigux/check-phase11-*.py`, `zigux/Makefile`, or the shared Phase 11 reminder surfaces.

Keep the current lane split explicit:
- bcm2835 lane `P11-L03` owns `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`
- gpio lane `P11-L06` owns `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`
- DesignWare lane `P11-L05` owns `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`
- HVC lane `P11-L16` owns `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey`
- header-boundary lane `P11-L18` owns `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, and the shared UAPI surface around `drivers/tty/hvc/hvc_console.h`

## Owner Split

Keep the current owner map explicit:
- shared packet truthfulness owns `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase11-shared-replay-contract.py`
- bcm2835 packet review owns `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` together with the bcm2835 validation matrix, survey, manifest-backed replay, and verify helper
- gpio packet review owns `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`
- DesignWare packet review owns `scripts/zigux/check-phase11-dw-wdt-packet.py`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `drivers/watchdog/dw_wdt_verify.zig`
- header-boundary truthfulness owns `scripts/zigux/check-phase11-header-boundary-packet.py`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_survey.zig`
- HVC archival replay owns `scripts/zigux/check-phase11-hvc-survey-packet.py`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`

## Shared Packet Surfaces

When a real Phase 11 change lands, keep these shared surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `zigux/Makefile`
- `make -C zigux phase11`
- `make -C zigux phase11-hvc-survey`

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, and header-boundary reminders into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the docs-root, scripts-root, tests-root, contract-checker, and make-route surfaces, while the driver-local evidence stays with the owning lane.
3. Keep the current validator posture explicit: there is no shared `make -C zigux phase11-validate` target or shared `validate-phase11.py` on `master`, so reminder-surface edits should stay aligned with the landed checker packet and make-backed replay routes instead of implying a broader validator stack.
4. Treat the header-boundary lane as shared public-surface evidence, not as a fifth driver port.
5. Do not imply broader registration, notifier, sysrq, khvcd, live cleanup, poweroff, reset, or hardware-backed parity closure beyond the lane-local notes and replays already shipped on `master`.
6. Keep the DesignWare lane honest: on current `master` the landed DesignWare packet is the validation matrix, survey note, teardown note, registration-scaffold replay, verify helper, dedicated packet checker, and shared Phase 11 replay route rather than a docs-only planning placeholder.
7. Keep the HVC lane honest: on current `master` the landed HVC archival packet is the survey gate, modem-control split, poll-retry split, sysrq helper, teardown note, validation matrix, and dedicated `phase11-hvc-survey` route rather than missing `hvc_console` starter, cleanup, manifest, or verify-helper files.

## Non-Goals

This note does not widen Phase 11 into:
- a claim that the overall simple-driver tranche is closed
- a dedicated shared validator stack beyond the landed packet checkers and make-backed replay routes
- broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, or khvcd execution
- a migration of driver-local teardown, survey, validation-matrix, or manifest ownership into the shared packet