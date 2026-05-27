# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current
Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_GPIO_WDT_STATUS=driver_docs_proof_and_current_head_manifest_truthful`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current gpio watchdog teardown and failure-mode packet honest
  without widening into live GPIO descriptor acquisition, platform-driver
  registration, watchdog-core registration, remove hooks, reboot-backed teardown
  execution, or hardware-backed validation

## Current Repo Reality

The current gpio watchdog matrix packet on `master` is:

- `drivers/watchdog/gpio_wdt.zig`
- `drivers/watchdog/gpio_wdt_verify.zig`
- `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
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

The older wider replay and route surfaces
`zigux/tests/phase11_gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
`zigux/tests/phase11_gpio_wdt_manifest.json`,
`zigux/tests/phase11_gpio_wdt_survey.zig`,
`Documentation/zigux/phase11-shared-replay-contract.md`, and
`zigux/tests/phase11_build.zig` are not part of the current `master` packet, so
this matrix keeps the lane grounded on the returned driver, proofs, dedicated
bounded replay routes, the machine-readable current-head manifest, and the
directly coupled docs surface only.

## Current Matrix

The returned driver, the driver-backed verify helper, focused preflight proof,
focused register-device glue proof, focused nowayout policy proof, focused
remove-handoff proof, dedicated bounded replay routes, plus the paired module
slice, teardown note, remove-handoff note, and machine-readable current-head
manifest keep the bounded gpio watchdog checkpoint names directly reviewable as
driver-backed teardown and failure-mode surfaces.

The focused current-head manifest survey adds one dedicated fail-closed route
for the recovered manifest packet without pretending that the older wider gpio
manifest or shared Phase 11 build route has returned.

The dedicated current-head manifest checker now keeps the recovered manifest
packet aligned through
`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`
and `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py`, so the
manifest, survey note, validation matrix, and dedicated survey build route have
one direct truthfulness guard on current `master`.

## Review Guardrails

- Treat this matrix as current-head truthfulness only, not as proof of live
  platform behavior or hardware-backed validation.
- Keep teardown and failure-mode parity bounded to the current driver, the
  driver-backed verify helper, direct proofs, dedicated replay routes, the
  machine-readable current-head manifest, and the directly coupled docs packet
  until a later repo change restores wider replay or build-route surfaces.
- Do not use this note to claim live GPIO descriptor acquisition,
  `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution,
  `watchdog_stop_on_reboot()` execution,
  `devm_watchdog_register_device()` execution, platform-driver registration,
  watchdog-core registration, live platform cleanup callbacks, live remove-hook
  execution, reboot-backed teardown execution, or hardware-validated parity.
- If a future repo change restores any wider gpio replay, the older wider
  `phase11_gpio_wdt_manifest.json` path, survey gate, or shared-route file,
  refresh this matrix together with the reopened companion surface in one
  bounded pass.

## Next Blocked Step

The next honest gpio-only follow-up is dedicated survey-gate recovery, the
older wider manifest return, or another equally small validation-truthfulness
repair, rather than new runtime behavior.
