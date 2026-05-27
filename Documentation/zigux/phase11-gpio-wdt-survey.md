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
  - `zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`
  - `zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
  - `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`
  - `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
  - `zigux/tests/phase11_gpio_wdt_current_head_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`
  - `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- older wider replay and manifest route surfaces such as
  `zigux/tests/phase11_gpio_wdt.zig`,
  `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
  `zigux/tests/phase11_gpio_wdt_manifest.json`,
  `zigux/tests/phase11_gpio_wdt_survey.zig`,
  `Documentation/zigux/phase11-shared-replay-contract.md`, and
  `zigux/tests/phase11_build.zig` still remain outside the returned
  current-head packet, so keep that deeper replay and shared-route packet framed
  as archival or repo-reality-gap vocabulary until a future reread proves those
  anchors returned beside the current direct proof files
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-gpio-wdt`
  route, but the returned packet now has dedicated bounded replay routes at
  `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`, and the
  current-head manifest survey route
  `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`
- remaining unported work is still wider focused replay, dedicated survey-gate
  recovery, the older wider manifest return, live platform-driver registration
  execution, live watchdog-core registration execution, live remove-hook
  execution, reboot-backed teardown execution, and hardware-backed validation

## Current-Head Packet

Treat the current bounded gpio watchdog packet on `master` as the returned
driver-plus-docs-plus-proof packet below:

- `drivers/watchdog/gpio_wdt.zig`
- `drivers/watchdog/gpio_wdt_verify.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`
- `zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_current_head_manifest.json`
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned driver, driver-backed verify helper, focused proofs, dedicated
bounded replay routes, and companion notes now also carry a machine-readable
current-head manifest that keeps the packet inventory explicit without
overclaiming that the older wider manifest or shared replay route has returned
on current `master`.

The dedicated registration-intent route now keeps timeout setup, nowayout
application, stop-on-reboot ordering, and pre-registration start posture
reviewable before the first register-device request, instead of leaving that
checkpoint implicit inside the broader register-device glue proof.

The focused current-head manifest survey now fail-closes on the recovered
manifest plus the coupled survey and validation matrix so this smaller packet
cannot drift silently while the wider archival manifest path stays absent.

`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`
and `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py`
now fail-closes on the recovered manifest, survey note, validation matrix, and
dedicated build route so this current-head packet keeps one directly readable
checker surface instead of leaving checker upkeep implicit.
