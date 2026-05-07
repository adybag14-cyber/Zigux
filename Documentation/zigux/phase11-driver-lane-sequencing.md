# Phase 11 Driver Lane Sequencing

This note turns the current `master` evidence for the Phase 11 simple-driver tranche into one bounded anti-overlap map for driver lanes only.

## Status

- `PHASE11_STATUS=parked`
- `PHASE11_SLICE=driver-lane-sequencing`
- lane: `P11-Y06`
- scope: use the current watchdog and `hvc_console` validation packets to say which Phase 11 driver lane owns which already-landed evidence and which next bounded step still belongs to that lane
- product boundary:
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`

## Why this note exists

The live repo already has four distinct Phase 11 driver packets:

- the `bcm2835_wdt` packet around `drivers/watchdog/bcm2835_wdt.zig`
- the `gpio_wdt` packet around `drivers/watchdog/gpio_wdt.zig`
- the `dw_wdt` packet around `drivers/watchdog/dw_wdt.zig`
- the `hvc_console` packet around `drivers/tty/hvc/hvc_console.zig`

Those packets now share `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `zigux/tests/phase11_build.zig`, the shared `make -C zigux phase11` route, and the workflow-backed replay contract, while the adjacent header-boundary and teardown reminders stay explicit beside them. That shared review surface is useful, but it also makes it easier for nearby runs to borrow each other's packet scope or reopen the wrong driver note.

This note keeps the Phase 11 driver tranche honest by separating shared replay routes from per-lane ownership.

## Shared packet versus lane ownership

Shared Phase 11 replay surface:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `zigux/tests/phase11_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

These shared docs, workflow-backed routes, and the shared contract checker prove that the current bounded Phase 11 starter still replays together and still fails closed when the shared review packet drifts. They do not change which lane owns a driver helper, validation matrix, manifest, survey gate, or next bounded follow-up.

The adjacent shared header-boundary packet also stays outside driver-lane ownership:

- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

Driver lanes may cite that shared packet when they explain current replay posture, but they should not absorb its checker or manifest scope.

## Lane map

`P11-L08` bcm2835 watchdog lane owns the bounded bcm2835 packet:

- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`

This lane may mention shared replay drift, but it does not own GPIO, DesignWare, HVC, or shared header-boundary follow-through. Its next honest work stays inside bcm2835 registration truthfulness, platform-handoff wording, or similarly narrow watchdog-local repairs.

The gpio watchdog lane owns GPIO-local starter and registration-handoff evidence:

- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt.zig`

This lane may cite shared watchdog replay coverage, but it does not own bcm2835 poweroff wording, DesignWare timeout-table follow-through, or HVC teardown evidence. Its next bounded work stays inside GPIO descriptor preflight, registration-facing handoff truthfulness, or another comparably small GPIO-local note.

The DesignWare watchdog lane owns the `dw_wdt` platform-facing starter:

- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt.zig`

This lane may compare its platform-backed follow-through against the other watchdog packets, but it does not own their manifests or next-step selection. Its next bounded work stays inside DesignWare registration, verify-backed handoff truthfulness, reset or clock ownership wording, or another direct `dw_wdt` handoff repair.

The HVC console lane owns console-local starter, survey, verify-backed, and teardown-adjacent evidence:

- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`

This lane may rely on the shared replay contract and may keep the bounded `hvc_cleanup()` teardown handoff, the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route, and the `make -C zigux phase11-hvc-survey` replay reviewable beside the driver-local teardown note, but it does not own watchdog-local registration, timeout, reset, or poweroff follow-through. Its next bounded work stays inside HVC registration, verify-backed notifier or sysrq truthfulness, or teardown-parity truthfulness.

## Anti-overlap rules

- If a Phase 11 run changes `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, the bcm2835 manifest, the bcm2835 survey gate, or the bcm2835 validation matrix, that work belongs to the bcm2835 lane.
- If a Phase 11 run changes `drivers/watchdog/gpio_wdt.zig`, the GPIO manifest, the GPIO survey gate, the GPIO module or slice notes, or the GPIO validation matrix, that work belongs to the GPIO watchdog lane.
- If a Phase 11 run changes `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, the DesignWare manifest, the DesignWare survey gate, or the DesignWare validation matrix, that work belongs to the DesignWare watchdog lane.
- If a Phase 11 run changes `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, the HVC manifest, the HVC survey gate, the dedicated HVC survey checker or its `make -C zigux phase11-hvc-survey` replay path, or the HVC validation matrix, that work belongs to the HVC console lane.
- If a Phase 11 run only changes `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the shared replay contract, the shared contract checker, the shared header-boundary packet, the shared build wiring, or the workflow-backed replay route, it should reopen the smallest directly coupled shared packet first instead of quietly consuming one of the driver lanes.
- Shared build or make replay drift should only reopen a driver lane when the break is actually rooted in that driver's helper, manifest, survey, or validation matrix.

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the bcm2835, GPIO, DesignWare, and HVC driver packets again. Any deeper helper, survey, or validation work should return to the owning driver lane instead of widening this note.
