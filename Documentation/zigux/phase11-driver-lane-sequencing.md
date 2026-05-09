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

Those packets now share `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `zigux/tests/phase11_build.zig`, the shared `make -C zigux phase11` route, and the workflow-backed replay contract, while the adjacent header-boundary and teardown reminders stay explicit beside them. That shared review surface is useful, but it also makes it easier for nearby runs to borrow each other's packet scope or reopen the wrong driver note.

This note keeps the Phase 11 driver tranche honest by separating shared replay routes from per-lane ownership.

## Shared packet versus lane ownership

Shared Phase 11 replay surface:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `zigux/tests/phase11_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

These shared docs, workflow-backed routes, the shared contract checker, and the shared closure note prove that the current bounded Phase 11 starter still replays together and still fails closed when the shared review packet drifts. They do not change which lane owns a driver helper, validation matrix, manifest, survey gate, or next bounded follow-up.

The adjacent shared header-boundary packet also stays outside driver-lane ownership:

- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

Driver lanes may cite that shared packet when they explain current replay posture, but they should not absorb its checker or manifest scope.

## Lane map

`P11-L10` now carries current scheduled continuity for the archived bcm2835 watchdog packet, whose packet identity remains `P11-L08` for traceability and whose current manifest state is still `blocked_on_driver_scaffold` for live platform registration:

- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`

This lane may mention shared replay drift and keep the dedicated bcm2835 packet checker explicit beside the archival survey packet, but it does not own GPIO, DesignWare, HVC, or shared header-boundary follow-through. Its next honest work stays inside bcm2835 registration truthfulness, current-lane continuity wording, platform-handoff wording, checker-backed packet truthfulness, or similarly narrow watchdog-local repairs. It should not consume DesignWare's broader platform-scaffold follow-through or HVC teardown truthfulness work just because those lanes also mention registration or cleanup boundaries.

`P11-L04` owns the GPIO watchdog lane, whose current manifest state is `blocked_on_driver_scaffold` for live platform registration and hardware-backed follow-through. It owns GPIO-local starter, registration-handoff evidence, teardown-note truthfulness, and the focused platform-drvdata replay:

- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt.zig`

This lane may cite shared watchdog replay coverage and keep the focused platform-drvdata replay explicit beside the shared packet, but it does not own bcm2835 poweroff wording, DesignWare timeout-table follow-through, or HVC teardown evidence. Its next bounded work stays inside GPIO descriptor preflight, registration-facing handoff truthfulness, focused platform-drvdata ordering truthfulness, teardown-parity truthfulness, or another comparably small GPIO-local note. It should stay parked on truthfulness or ordering repairs until the lane can carry an explicit registration scaffold instead of borrowing the DesignWare lane's more advanced platform-shape wording.

`P11-L12` owns the DesignWare watchdog lane. This is the only current Phase 11 driver lane whose manifest still carries an explicit `ready_next` handoff, namely `phase11-dw-wdt-live-platform-pm`. It owns the `dw_wdt` platform-facing starter, its dedicated packet checker, its registration-scaffold replay, and its teardown ownership note:

- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt.zig`

This lane may compare its platform-backed follow-through against the other watchdog packets, but it does not own their manifests, HVC teardown follow-through, or next-step selection. Its next bounded work stays inside DesignWare registration, dedicated packet-checker truthfulness, registration-scaffold truthfulness, verify-backed handoff truthfulness, teardown-parity truthfulness, reset or clock ownership wording, or another direct `dw_wdt` handoff repair. If any Phase 11 driver lane gets the next broader platform-backed execution slice, it should be this one, because the repo already records the matching `ready_next` marker here and not in the other driver manifests.

`P11-L16` owns the HVC console lane. Its current manifest is fully `starter_landed`, so its near-term work is anti-drift truthfulness only rather than another broadening scaffold. It owns console-local starter, slice, survey, archival-manifest, dedicated survey-checker-backed, verify-backed, and teardown-adjacent evidence:

- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`

This lane may rely on the shared replay contract and may keep the bounded `hvc_cleanup()` teardown handoff, the bounded khvcd polling-contract and `hvc_hangup()` disconnect truthfulness, the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival checker, and the checker-backed `make -C zigux phase11-hvc-survey` replay reviewable beside the driver-local teardown note, but it does not own watchdog-local registration, timeout, reset, or poweroff follow-through. Its next bounded work stays inside HVC registration, verify-backed notifier or sysrq truthfulness, khvcd polling-contract or hangup-disconnect truthfulness, or teardown-parity truthfulness. It should not absorb shared support-packet cleanup unless the drift is specifically HVC-local.

## Anti-overlap rules

- If a Phase 11 run changes `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, the bcm2835 manifest, the bcm2835 survey gate, the bcm2835 validation matrix, or the dedicated bcm2835 packet checker, that work belongs to the bcm2835 lane.
- If a Phase 11 run changes `drivers/watchdog/gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, the GPIO manifest, the GPIO survey gate, the GPIO module or slice notes, or the GPIO validation matrix, that work belongs to the GPIO watchdog lane.
- If a Phase 11 run changes `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, the DesignWare manifest, the DesignWare survey gate, or the DesignWare validation matrix, that work belongs to the DesignWare watchdog lane.
- If a Phase 11 run changes `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, the HVC manifest, the HVC survey gate, the dedicated HVC survey checker or its `make -C zigux phase11-hvc-survey` replay path, or the HVC validation matrix, that work belongs to the HVC console lane.
- If a Phase 11 run only changes `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the shared replay contract, the shared closure note, the shared contract checker, the shared header-boundary packet, the shared build wiring, or the workflow-backed replay route, it should reopen the smallest directly coupled shared packet first instead of quietly consuming one of the driver lanes.
- Shared build or make replay drift should only reopen a driver lane when the break is actually rooted in that driver's helper, manifest, survey, validation matrix, named teardown ownership note, dedicated packet checker, or the focused gpio platform-drvdata replay.

## Current sequencing decision

- `P11-L12` DesignWare is the only Phase 11 driver lane allowed to claim the next broader execution-facing follow-up today, because `zigux/tests/phase11_dw_wdt_manifest.json` is the only current driver manifest that still records a `ready_next` marker.
- `P11-L04` GPIO and `P11-L10` or `P11-L08` bcm2835 both remain blocked on driver scaffold for any live platform-registration widening, so nearby runs should keep them to truthfulness, ordering, teardown-note, validation-matrix, or checker-backed packet repairs.
- `P11-L16` HVC remains starter-landed and anti-drift only, so nearby runs should keep it to notifier, sysrq, khvcd, hangup, teardown-note, survey-note, validation-matrix, or archival-checker truthfulness rather than treating it as the next broad Phase 11 execution lane.
- `P11-Y06` should therefore stay parked after recording this owner map unless repo drift blurs these boundaries again.

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the bcm2835, GPIO, DesignWare, and HVC driver packets again. Any deeper helper, survey, or validation work should return to the owning driver lane instead of widening this note.
