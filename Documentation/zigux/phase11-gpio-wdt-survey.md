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
  - `drivers/watchdog/gpio_wdt_verify.zig`
  - `zigux/tests/phase11_gpio_wdt_preflight_review.zig`
  - `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
  - `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`
  - `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
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
  reread proves those anchors returned beside the current direct proof files
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-gpio-wdt`
  route, but the returned packet now has dedicated bounded replay routes at
  `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`, and
  `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
- remaining unported work is still wider focused replay or manifest recovery,
  live platform-driver registration execution, live watchdog-core registration
  execution, live remove-hook execution, reboot-backed teardown execution, and
  hardware-backed validation

## Current-Head Packet

Treat the current bounded gpio watchdog packet on `master` as the returned
driver-plus-docs-plus-proof packet below:

- `drivers/watchdog/gpio_wdt.zig`
- `drivers/watchdog/gpio_wdt_verify.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned driver, driver-backed verify helper, focused preflight proof,
focused register-device glue proof, focused nowayout policy proof, focused
remove-handoff proof, dedicated bounded replay routes, and companion notes keep
the bounded `platformDriverIdentitySummary()`, `watchdogMetadataSummary()`,
`probeSummary()`, `descriptorRequestSummary()`,
`descriptorPreflightSummary()`, `timeoutPropertyCheckpointSummary()`,
`platformDrvdataCheckpointSummary()`, `watchdogDrvdataCheckpointSummary()`,
`registrationIntentCheckpointSummary()`, `rebootGlueCheckpointSummary()`,
`nowayoutPolicySummary()`, `registrationHandoffSummary()`,
`registrationPlanSummary()`, `registerDeviceCallSummary()`,
`registerDeviceFailureSummary()`, `requestStop()`, `summarizeTeardown()`,
`platformCleanupCheckpointSummary()`, and `summarizeRemoveHandoff()` checkpoint
names reviewable as the current packet.

That means the roadmap-facing simple-driver template, bounded teardown parity,
and bounded failure-mode parity are already reviewable in the returned packet,
while live execution and hardware-backed validation stay outside the current
claim.

The driver-backed verify helper keeps `registrationPlanSummary()`,
`registerDeviceCallSummary()`, `registerDeviceFailureSummary()`,
`rebootGlueCheckpointSummary()`, `summarizeTeardown()`, and
`summarizeRemoveHandoff()` directly replayable beside the focused proofs without
claiming live GPIO, watchdog-core registration, remove-hook execution, or
shutdown execution.

The direct preflight proof now exercises `descriptorPreflightSummary()`
alongside the timeout-property and drvdata-ordering checkpoints without
claiming live descriptor acquisition, reboot glue execution, or watchdog-core
registration.

The direct nowayout proof now exercises `nowayoutPolicySummary()` across the
bounded stopped, blocked-by-nowayout, and kept-running dispositions without
claiming live watchdog-core registration or teardown execution.

The direct remove-handoff proof now exercises
`platformCleanupCheckpointSummary()` and `summarizeRemoveHandoff()` as a
dedicated bounded replay before any live cleanup callback,
platform-driver-removal, watchdog-core-unregister, or shutdown-execution claim.

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
packet directly reviewable on `master` through the returned driver, the
driver-backed verify helper, the focused preflight proof, the focused
register-device glue proof, the focused nowayout policy proof, the focused
remove-handoff proof, the dedicated bounded replay routes, and the survey note,
module slice, teardown note, remove-handoff note, and validation matrix.

That current packet now also keeps the bounded remove-handoff packet explicit
beside the existing watchdog-drvdata ownership handoff, reboot-glue
checkpoint, direct nowayout-policy proof, and a dedicated cleanup-to-remove
replay without overstating live unregister or shutdown behavior.

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
manifest recovery, checker upkeep, or another equally small truthfulness
repair.
