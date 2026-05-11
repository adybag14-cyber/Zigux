# Phase 11 Shared Replay Contract

This note records the bounded shared replay surface for the active Phase 11 simple-driver tranche on `master`.
It stays inside the shared closure packet that is already landed and reviewable, and it does not promote any driver-local next step into a broader Phase 11 closure claim.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`
* compatibility marker for the coupled header-boundary checker: `PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable`
* scope: keep the active Phase 11 simple-driver shared packet honest while the roadmap still keeps broader teardown, failure-mode parity, and execution-facing follow-through inside the owning driver lanes

## Roadmap Anchor

* the product roadmap still defines Phase 11 as the simple-production-driver tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
* the shared packet should only name review surfaces that keep the landed simple-driver tranche replayable together on `master`
* driver-local teardown, manifest, validation-matrix, registration, notifier, sysrq, khvcd, reset, clock, poweroff, and platform-backed follow-through still belong to the owning Phase 11 driver lanes

## Shared Replay Surface On `master`

The active shared Phase 11 packet is the docs-root, closure-note, owner-map, checker, workflow, and replay surface that keeps the already-landed starter packet reviewable together:

* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-closure-note.md`
* `Documentation/zigux/phase11-driver-lane-sequencing.md`
* `scripts/zigux/README.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `scripts/zigux/check-phase11-header-boundary-packet.py`
* `zigux/tests/README.md`
* `zigux/tests/phase11_build.zig`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`
* `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* `make -C zigux phase11`
* `make -C zigux phase11-hvc-survey`

These shared docs, the workflow-backed routes, the shared contract checker, the shared header-boundary checker, the shared closure note, and the shared driver-lane owner map prove that the current bounded Phase 11 starter still replays together and still fails closed when the shared review packet drifts.
There is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`.
There is no broader multi-checker Phase 11 validator stack on `master`.
There is no shared `validate-phase11.py` in the current shared packet on `master`.
There is no shared `make -C zigux phase11-validate` target on `master`.

The live gpio watchdog evidence inside that shared route stays explicit through `Documentation/zigux/phase11-gpio-wdt-module-slice.md`.
The dedicated gpio watchdog archival packet beside that slice also stays explicit through `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`.
That bounded slice keeps the `gpio_wdt_lab` descriptor, timeout-property, drvdata-ordering, register-device preflight, teardown, and failure-mode packet reviewable without claiming live GPIO descriptor acquisition, watchdog-core registration, or hardware-backed validation.
The shipped bcm2835 watchdog sub-packet inside that shared route stays explicit through `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`.
The current DesignWare lane inside that shared route stays explicit through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`.
That bounded planning lane keeps the first platform-registration follow-through visible beside the shared route without claiming a landed validation matrix, teardown note, manifest-backed replay, verify helper, dedicated checker, or MMIO-backed validation packet on current `master`.
The shipped shared header-boundary companion inside that same route stays explicit through `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, and `scripts/zigux/check-phase11-header-boundary-packet.py`.
This shared public-header packet keeps the bounded `watchdog_info`, `winsize`, and exported `drivers/tty/hvc/hvc_console.h` helper declaration survey visible beside the watchdog and HVC driver-local packets without collapsing it back into the dedicated `hvc_console` archival note.

## Driver-Local Evidence That Stays Beside The Shared Route

The shared replay surface keeps the simple-driver tranche visible together, but the detailed evidence still stays with the owning lane packet instead of being absorbed into this note:

* gpio watchdog: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`
* bcm2835 watchdog: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
* DesignWare planning lane: `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`

The dedicated archival HVC evidence still stays explicit beside that shared route:

* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `make -C zigux phase11-hvc-survey`

These paths keep the bounded HVC manifest-backed survey, modem-control split, poll-retry split, sysrq-handoff helper, and dedicated survey route reviewable beside the shared route without promoting missing driver-starter, cleanup replay, compile-local verify-helper, tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, or host-backed cleanup into the current shared contract.
That driver-local execution follow-through still belongs to the owning Phase 11 HVC lane rather than this shared replay contract.

## What This Contract Does Not Claim

* no broader shared validator stack beyond the landed `scripts/zigux/check-phase11-shared-replay-contract.py` and `scripts/zigux/check-phase11-header-boundary-packet.py` packet for this shared replay note
* no driver-local next-step widening beyond the active shared replay packet
* no landed DesignWare validation matrix, teardown note, manifest-backed replay, verify helper, or dedicated packet checker beyond the planning note already parked on current `master`
* no tty-driver starter, cleanup replay, compile-local verify helper, tty registration, notifier execution, sysrq execution, khvcd execution, host-backed cleanup, live platform registration, live clock or reset ownership, live IRQ registration, or hardware-backed watchdog validation beyond the landed bcm2835 and gpio packets plus the landed HVC archival replay surfaces

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest shared-packet truthfulness repair.
Prefer a docs-root, closure-note, owner-map, checker, or shared replay-route sync only when the active simple-driver tranche drifts across those already-shipped shared surfaces.
Driver-local survey, manifest, teardown-note, validation-matrix, scaffold, or helper follow-through should return to the owning lane instead of widening this contract.
