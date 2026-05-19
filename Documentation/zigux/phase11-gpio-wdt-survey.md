# Phase 11 GPIO Watchdog Survey

This note keeps the bounded Phase 11 `gpio_wdt` packet truthful on current
`master`.
It stays inside the simple-driver lane and records the smaller docs-only
current-head packet that remains directly reviewable after older gpio watchdog
starter-depth wording drifted ahead of current contents reads.

## Status

- `PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_docs_packet_truthful`
- lane: `P11-L01`
- reviewed against live `master`
- the Phase 11 roadmap still keeps `drivers/watchdog/gpio_wdt.c` inside bounded
  simple-production-driver work where teardown parity and failure-mode
  reviewability should deepen before any live execution claims
- current authenticated contents readback keeps the bounded gpio watchdog packet
  reviewable through:
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- current authenticated contents readback still does not rematerialize
  `drivers/watchdog/gpio_wdt.zig`,
  `zigux/tests/phase11_gpio_wdt.zig`,
  `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
  `zigux/tests/phase11_gpio_wdt_manifest.json`,
  `zigux/tests/phase11_gpio_wdt_survey.zig`,
  `Documentation/zigux/phase11-shared-replay-contract.md`, or
  `zigux/tests/phase11_build.zig`, so keep that older starter-depth packet
  framed as archival or repo-reality-gap vocabulary until a future reread proves
  those deeper anchors returned
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-gpio-wdt`
  route
- remaining unported work is still direct driver readback, focused replay or
  manifest recovery, platform-driver registration reviewability, watchdog-core
  registration reviewability, remove-hook reviewability, reboot-backed teardown
  execution, and hardware-backed validation

## Current-Head Packet

Treat the current bounded gpio watchdog packet on `master` as the smaller
current-head docs packet below:

- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned module slice, teardown note, and validation matrix still keep the
bounded `descriptorRequestSummary()`,
`platformDrvdataCheckpointSummary()`, `nowayoutPolicySummary()`,
`registrationHandoffSummary()`, `registrationPlanSummary()`,
`registerDeviceCallSummary()`, `registerDeviceFailureSummary()`,
`requestStop()`, and `summarizeTeardown()` checkpoint names reviewable as the
current docs-backed packet.

## Still-Bounded Gaps

Keep the deeper driver file, focused replay, platform-drvdata replay, manifest,
dedicated survey gate, shared replay contract, and shared Phase 11 build route
framed as archival or repo-reality-gap vocabulary until a future reread proves
those surfaces returned beside this smaller docs packet.

Keep `zigux/Makefile` explicit only as the returned file; it still does not
prove a dedicated `make -C zigux phase11-gpio-wdt` route.

Keep the lane below live GPIO descriptor execution, `platform_set_drvdata()`
execution, `watchdog_set_drvdata()` execution,
`devm_watchdog_register_device()` execution, platform-driver registration,
watchdog-core registration, remove-hook parity, reboot-backed teardown, and
hardware-backed validation.

## What Landed

Current authenticated contents reads keep a narrower gpio watchdog continuity
packet directly reviewable on `master` through the survey note, module slice,
teardown note, and validation matrix.

This survey therefore keeps the current-head packet honest without reviving the
older driver, replay, manifest, shared-contract, or survey-gate anchors as if
they had all returned.

## Bounded Meaning

This note records that the gpio watchdog simple-driver lane still has reviewable
current-head continuity through the docs-backed checkpoint packet listed above.

It does not claim live GPIO descriptor acquisition, drvdata execution,
watchdog-core registration side effects, remove-hook behavior, reboot-backed
shutdown execution, or hardware-validated teardown parity.

If a future reread rematerializes the deeper gpio driver, replay, manifest, or
checker anchors, refresh this survey together with the validation matrix and the
smallest directly coupled gpio reminder surface in one bounded pass.
