# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes so shared reminders do not collapse bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-surface follow-through into one noisy bucket.

## Scope

Use this note when a Phase 11 change touches any part of the shared reminder packet under `Documentation/zigux/phase11-*.md`, `scripts/zigux/check-phase11-*.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the shared contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

* shared sequencing lane `P11-Y06` owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, and `scripts/zigux/check-phase11-shared-summary-surfaces.py`, plus the shared `zigux/tests/fixtures/phase11_build_inventory.json` anchor, the shared `zigux/Makefile` reminder surface, the direct `make -C zigux phase11-contract` route, and the shared Phase 11 workflow markers in `.github/workflows/zigux-bootstrap.yml`
* bcm2835 lane `P11-L08` owns bcm2835 reminder-note and checker follow-through; keep the landed direct bcm2835 replay files explicit in shared summaries without widening them into broader poweroff or PM closure claims
* gpio lane `P11-L04` owns gpio watchdog reminder-note and checker follow-through; keep the landed direct gpio replay files explicit in shared summaries without widening them into broader hardware-backed closure claims
* DesignWare lane `P11-L10` owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig` as the surviving bounded DesignWare packet; keep the landed direct DesignWare replay files and compile-local teardown or restart proofs explicit in shared summaries without widening them into broader platform-registration closure claims
* HVC archival packet lane `P11-L16` owns HVC reminder-note and checker follow-through; keep the landed archival packet explicit through `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey` without widening that bounded archival packet into notifier, khvcd, or host-backed execution closure claims
* HVC driver-follow-through lane `P11-Y04` owns direct `drivers/tty/hvc/hvc_console.zig` reopen work only when that driver-local file is materially present and moving
* contributor-note lane `P11-L18` owns the shared contributor-facing wording across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
* shared header-boundary evidence stays split: deterministic checker drift belongs to `P11-L11` through `scripts/zigux/check-phase11-header-boundary-packet.py`, while the public header-boundary reminder note stays adjacent shared evidence rather than HVC or contributor-note ownership

## Shared Packet Boundaries

The shared Phase 11 packet still living together on current `master` is the reminder-and-checker stack:

* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-closure-note.md`
* `Documentation/zigux/phase11-driver-lane-sequencing.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `scripts/zigux/check-phase11-shared-summary-surfaces.py`
* `zigux/tests/fixtures/phase11_build_inventory.json`
* `zigux/Makefile`
* `make -C zigux phase11-contract`
* `.github/workflows/zigux-bootstrap.yml`

Direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig` and some direct watchdog or HVC replay files, but the contents bridge still materializes `zigux/tests/fixtures/phase11_build_inventory.json` and raw GitHub fallback materializes the current shared build file plus the direct watchdog and HVC replay files on `master`, so the shared sequencing lane should keep those paths explicit as landed bounded replay evidence rather than treating them as repo-reality gaps.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-note reminder work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the shared notes, the shared contract checker, the shared summary-surfaces checker, the shared `zigux/tests/fixtures/phase11_build_inventory.json` anchor, the shared `zigux/Makefile` reminder surface including `make -C zigux phase11-contract`, the shared Phase 11 workflow markers in `.github/workflows/zigux-bootstrap.yml`, and the landed bounded build-and-replay packet while driver-local reminder-note ownership stays separate.
3. Keep the shared sequencing lane honest: `P11-Y06` may repair only the shared packet truthfulness surfaces and must not absorb driver-local reminder-note work or contributor-note wording unless those owner lanes are the things moving.
4. Keep the current validator posture explicit: there is no shared `validate-phase11.py`, the shared `zigux/tests/fixtures/phase11_build_inventory.json` is materialized and should stay explicit beside `zigux/tests/phase11_build.zig`, and the direct contents bridge can still 404 on `zigux/tests/phase11_build.zig`, so reminder-surface edits should preserve the raw-fallback materialization story, keep the shipped `make -C zigux phase11-contract` route explicit as the shared checker-backed reminder entrypoint, and avoid downgrading the landed inventory-backed build packet into an unshipped gap.
5. Treat the shared header-boundary packet as adjacent public-surface evidence, not as a fifth driver port; keep deterministic checker drift with `P11-L11` and contributor-note wording with `P11-L18` instead of folding either surface into the HVC lane.
6. Do not imply broader registration, notifier, sysrq, khvcd, live cleanup, poweroff, reset, or hardware-backed parity closure beyond the reminder notes and the bounded replay files currently materialized on `master`.
7. Keep the DesignWare lane honest: on current `master` the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`, pinned to `P11-L10`, while the next bounded step still remains platform-backed registration scaffolding rather than reviving removed manifest-backed reminder surfaces or widening the compile-local teardown or restart proofs into hardware-backed closure.
8. Keep the next bounded shared follow-through inside the smallest reminder-surface truthfulness repair unless a new shared summary or checker surface drifts again.

## Non-Goals

This note does not widen Phase 11 into:

* a claim that the overall simple-driver tranche is closed
* a dedicated shared validator or replay stack beyond the landed reminder checkers, the inventory-backed shared build packet, Makefile and workflow route markers, and the bounded replay files already materialized on `master`
* broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, or khvcd execution
* a migration of driver-local reminder-note ownership into the shared packet
