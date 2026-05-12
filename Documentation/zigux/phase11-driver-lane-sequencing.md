# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes so shared reminders do not collapse bcm2835, gpio, DesignWare, HVC, and shared header evidence into one noisy bucket.

## Scope

Use this note when a Phase 11 change touches any part of the shipped simple-driver packet under `drivers/watchdog/*.zig`, `drivers/tty/hvc/*.zig`, `Documentation/zigux/phase11-*.md`, `scripts/zigux/check-phase11-*.py`, `zigux/Makefile`, or the shared Phase 11 reminder surfaces.

Keep the current lane split explicit:
- shared sequencing lane `P11-Y06` owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, and `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- bcm2835 lane `P11-L03` owns `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`
- gpio lane `P11-L06` owns `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`
- DesignWare lane `P11-L05` currently owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`; `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` stay recorded as the intended first scaffold packet rather than shipped current-`master` evidence
- HVC delivery-gate lane `P11-L16` owns `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey`
- contributor-note lane `P11-L18` owns the shared reminder wording follow-up across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` when Phase 11 contributor-facing wording moves
- shared header-boundary evidence stays split: deterministic checker-chain drift belongs to `P11-L11` through `scripts/zigux/check-phase11-header-boundary-packet.py`, while `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_survey.zig` stay as adjacent shared public-surface evidence rather than HVC or contributor-note ownership

## Owner Split

Keep the current owner map explicit:
- shared packet truthfulness lane `P11-Y06` owns `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, and `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- bcm2835 packet review owns `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` together with the bcm2835 validation matrix, survey, manifest-backed replay, and verify helper
- gpio packet review owns `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`
- DesignWare packet review stays parked on `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`; `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` stay recorded as repo-reality gaps until the first scaffold lands
- shared header-boundary deterministic tooling stays with `P11-L11` for `scripts/zigux/check-phase11-header-boundary-packet.py`, while the dedicated survey note plus manifest-backed survey stay packet-local shared evidence and contributor-facing wording follow-up stays with `P11-L18`
- HVC delivery-gate replay stays with `P11-L16` through `scripts/zigux/check-phase11-hvc-survey-packet.py`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`

The shared packet surfaces still living together on current `master` are `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, and `make -C zigux phase11`.

## Shared Packet Surfaces

When a real Phase 11 shared reminder-surface change lands, keep these shared surfaces aligned:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- `zigux/tests/phase11_build.zig`
- `make -C zigux phase11`

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, and header-boundary reminders into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the shared notes, the shared contract checker, the shared `phase11_build.zig` route, and `make -C zigux phase11`, while `scripts/zigux/check-phase11-shared-summary-surfaces.py` remains the focused direct audit for the docs-root, scripts-root, tests-root, and checklist summaries when reminder wording moves.
3. Keep the shared sequencing lane honest: `P11-Y06` may repair only the shared packet truthfulness surfaces and must not absorb, rename, or edit driver-local bcm2835, gpio, DesignWare, HVC, or header-boundary evidence unless the matching owner lane is the one moving.
4. Keep the current validator posture explicit: there is a shared `zigux/tests/phase11_build.zig` route and a shared `make -C zigux phase11` wrapper on current `master`, but there is no shared `validate-phase11.py`, no shared `zigux/tests/fixtures/phase11_build_inventory.json`, and no shared `make -C zigux phase11-validate` target, so reminder-surface edits should stay aligned with the surviving build-backed packet instead of reviving the older inventory-driven validator story.
5. Treat the shared header-boundary packet as public-surface evidence, not as a fifth driver port; keep deterministic checker drift with `P11-L11` and contributor-note wording with `P11-L18` instead of folding either surface into the HVC lane.
6. Do not imply broader registration, notifier, sysrq, khvcd, live cleanup, poweroff, reset, or hardware-backed parity closure beyond the lane-local notes and replays already shipped on `master`.
7. Keep the DesignWare lane honest: on current `master` the landed DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` only, while `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` remain repo-reality gaps rather than a landed packet.
8. Keep the HVC delivery-gate lane honest: on current `master` the landed HVC archival packet is the teardown-note cleanup handoff through `zigux/tests/phase11_hvc_cleanup.zig`, the direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, the manifest-backed survey gate, modem-control split, poll-retry split, sysrq helper, validation matrix, and dedicated `phase11-hvc-survey` route rather than a missing or purely reminder-only packet.

## Non-Goals

This note does not widen Phase 11 into:
- a claim that the overall simple-driver tranche is closed
- a dedicated shared validator or replay stack beyond the landed reminder checkers plus the shared build-backed replay route
- broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, or khvcd execution
- a migration of driver-local teardown, survey, validation-matrix, or manifest ownership into the shared packet
