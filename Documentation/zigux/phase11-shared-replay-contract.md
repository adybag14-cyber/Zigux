# Phase 11 Shared Replay Contract

This note records only the Phase 11 simple-driver review surfaces that were directly re-verified on live `master` during Slot 215. It intentionally avoids claiming landed HVC or watchdog teardown artifacts that were not readable from current `master` in that repo-first check.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=contract_truthfulness_repair`
* scope: keep the Phase 11 simple-driver lane honest while the roadmap still asks for teardown and failure-mode parity, without overstating missing HVC or watchdog evidence as landed `master` state

## Roadmap Anchor

* the product roadmap still defines Phase 11 as the simple-production-driver tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
* the required evidence remains hardware-validation matrix coverage plus teardown and failure-mode parity
* this contract update stays inside that bounded review-surface lane and does not widen into tty registration, khvcd execution, notifier execution, sysrq execution, watchdog-core glue, or host-backed teardown behavior

## Re-Verified Surfaces On `master`

* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/phase11-shared-replay-contract.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `.github/workflows/zigux-bootstrap.yml`

## Missing Or Unverified Phase 11 HVC Surfaces

Direct GitHub content reads against live `master` returned `404` for each of these HVC-facing Phase 11 paths during this run:

* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `drivers/tty/hvc/hvc_console.zig`
* `drivers/tty/hvc/hvc_console_verify.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `zigux/tests/phase11_build.zig`
* `zigux/tests/phase11_hvc_console.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_survey.zig`

The same repo-first check also returned `404` for several broader Phase 11 review-surface paths that older reminders still describe as shipped, including:

* `zigux/tests/phase11_gpio_wdt_manifest.json`
* `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
* `Documentation/zigux/phase11-uapi-header-parity-survey.md`
* `scripts/zigux/check-phase11-header-boundary-packet.py`
* `zigux/Makefile`

## Shared Replay Commands

No executable Phase 11 build or make replay command was re-verified from a readable backing file on live `master` in this run.

Treat older references to these commands as historical or branch-local until their backing files are readable on `master` again:

* `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* `make -C zigux phase11`
* `make -C zigux phase11-hvc-survey`

## What This Contract Does Not Claim

* no landed HVC teardown or failure-mode packet on `master` beyond the high-level roadmap and reminder surfaces re-read above
* no landed watchdog validation-matrix, manifest, or scaffold packet that was directly re-read in this run
* no shipped `validate-phase11.py` or broader Phase 11 validator stack on `master`
* no tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, watchdog-core glue, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 work should stay inside the next smallest same-lane truthfulness repair.

Prefer one of these bounded follow-through steps:

* land one actual `master`-readable HVC teardown or failure-mode artifact and then wire this contract back to that concrete file
* restore one missing watchdog or HVC review surface at a time on `master` instead of restating a full shared starter packet from stale branch history

## Footer
