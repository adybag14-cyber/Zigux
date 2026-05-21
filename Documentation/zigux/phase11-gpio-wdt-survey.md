# Phase 11 GPIO Watchdog Survey

This note keeps the bounded Phase 11 `gpio_wdt` packet truthful on current
`master`.
It stays inside the simple-driver lane and records the smaller current-head
packet that remains directly reviewable after older gpio watchdog starter-depth
wording drifted ahead of current contents reads.

## Status

- `PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`
- lane: `P11-L04`
- reviewed against live `master`
- the Phase 11 roadmap still keeps `drivers/watchdog/gpio_wdt.c` inside bounded
  simple-production-driver work where teardown parity and failure-mode
  reviewability should deepen before any live execution claims
- current authenticated contents readback keeps the bounded gpio watchdog packet
  reviewable through:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- current authenticated contents readback still does not rematerialize the older
  wider replay and manifest route surfaces such as
  `zigux/tests/phase11_gpio_wdt.zig`,
  `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
  `zigux/tests/phase11_gpio_wdt_manifest.json`,
  `zigux/tests/phase11_gpio_wdt_survey.zig`,
  `Documentation/zigux/phase11-shared-replay-contract.md`, or
  `zigux/tests/phase11_build.zig`, so keep that deeper replay and manifest
  packet framed as archival or repo-reality-gap vocabulary until a future
  reread proves those anchors returned beside the current direct proof file
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-gpio-wdt`
  route
- remaining unported work is still direct focused replay or manifest recovery,
  platform-driver registration reviewability, watchdog-core registration
  reviewability, live remove-hook execution, reboot-backed teardown execution,
  and hardware-backed validation

## Current-Head Packet

Treat the current bounded gpio watchdog packet on `master` as the returned
driver-plus-docs-plus-proof packet below:

- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned driver, focused register-device glue proof, and companion notes
keep the bounded `platformDriverIdentitySummary()`,
`watchdogMetadataSummary()`, `probeSummary()`,
`descriptorRequestSummary()`, `timeoutPropertyCheckpointSummary()`,
`platformDrvdataCheckpointSummary()`,
`watchdogDrvdataCheckpointSummary()`, `rebootGlueCheckpointSummary()`,
`nowayoutPolicySummary()`, `registrationHandoffSummary()`,
`registrationPlanSummary()`, `registerDeviceCallSummary()`,
`registerDeviceFailureSummary()`, `requestStop()`, and `summarizeTeardown()`
checkpoint names reviewable as the current packet.

## Still-Bounded Gaps

Keep the older wider focused replay, platform-drvdata replay, manifest,
dedicated survey gate, shared replay contract, and shared Phase 11 build route
framed as archival or repo-reality-gap vocabulary until a future reread proves
those surfaces returned beside this smaller driver-plus-docs-plus-proof packet.

Keep `zigux/Makefile` explicit only as the returned file; it still does not
prove a dedicated `make -C zigux phase11-gpio-wdt` route.

Keep the lane below live GPIO descriptor execution, `platform_set_drvdata()`
execution, `watchdog_set_drvdata()` execution,
`watchdog_stop_on_reboot()` execution,
`devm_watchdog_register_device()` execution, platform-driver registration,
watchdog-core registration, live remove-hook execution, reboot-backed teardown,
and hardware-backed validation.

## What Landed

Current authenticated contents reads keep a narrower gpio watchdog continuity
packet directly reviewable on `master` through the returned driver, the focused
register-device glue proof, and the survey note, module slice, teardown note,
remove-handoff note, and validation matrix.

That current packet now also keeps the bounded remove-handoff packet explicit
beside the existing watchdog-drvdata ownership handoff and reboot-glue
checkpoint without overstating live unregister or shutdown behavior.

## Bounded Meaning

This note records that the gpio watchdog simple-driver lane still has reviewable
current-head continuity through the driver-plus-docs-plus-proof packet listed
above.

It does not claim live GPIO descriptor acquisition, drvdata execution,
watchdog-core registration side effects, live remove-hook execution,
reboot-backed shutdown execution, or hardware-validated teardown parity.

If a future reread rematerializes the deeper gpio replay, manifest, or checker
anchors, refresh this survey together with the validation matrix and the
smallest directly coupled gpio reminder surface in one bounded pass. If the
current smaller packet needs one more driver-local follow-up first, keep it to
focused replay recovery or another equally small truthfulness repair.