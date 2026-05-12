# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes so shared reminders do not collapse bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-surface follow-through into one noisy bucket.

## Scope

Use this note when a Phase 11 change touches any part of the shared reminder packet under `Documentation/zigux/phase11-*.md`, `scripts/zigux/check-phase11-*.py`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the shared contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

* shared sequencing lane `P11-Y06` owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, and `scripts/zigux/check-phase11-shared-summary-surfaces.py`, plus the shared Phase 11 route markers in `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml`
* bcm2835 lane `P11-L08` owns bcm2835 reminder-note and checker follow-through; treat direct bcm2835 Zig replay files as repo-reality gaps until they are materialized again on `master`
* gpio lane `P11-L04` owns gpio watchdog reminder-note and checker follow-through; treat direct gpio Zig replay files as repo-reality gaps until they are materialized again on `master`
* DesignWare lane `P11-L10` owns DesignWare reminder-note and checker follow-through; treat direct DesignWare Zig replay files as repo-reality gaps until they are materialized again on `master`
* HVC archival packet lane `P11-L16` owns HVC reminder-note and checker follow-through; treat direct HVC Zig replay files plus `drivers/tty/hvc/hvc_console_verify.zig` as repo-reality gaps until they are materialized again on `master`
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
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

Direct GitHub contents reads do not currently materialize `zigux/tests/phase11_build.zig` or the previously referenced direct watchdog and HVC replay files, so the shared sequencing lane must keep treating those paths as repo-reality gaps rather than as shipped replay evidence.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-note reminder work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the shared notes, the shared contract checker, the shared summary-surfaces checker, and the shared Phase 11 route markers in `zigux/Makefile` plus `.github/workflows/zigux-bootstrap.yml` while the direct build and replay files remain absent.
3. Keep the shared sequencing lane honest: `P11-Y06` may repair only the shared packet truthfulness surfaces and must not absorb driver-local reminder-note work or contributor-note wording unless those owner lanes are the things moving.
4. Keep the current validator posture explicit: there is no shared `validate-phase11.py`, no shared `zigux/tests/fixtures/phase11_build_inventory.json`, and no materialized shared `zigux/tests/phase11_build.zig` on current `master`, so reminder-surface edits should stay aligned with the surviving reminder packet instead of reviving an unshipped build-backed replay story.
5. Treat the shared header-boundary packet as adjacent public-surface evidence, not as a fifth driver port; keep deterministic checker drift with `P11-L11` and contributor-note wording with `P11-L18` instead of folding either surface into the HVC lane.
6. Do not imply broader registration, notifier, sysrq, khvcd, live cleanup, poweroff, reset, or hardware-backed parity closure beyond the reminder notes and checkers currently materialized on `master`.
7. Keep the next bounded shared follow-through inside the smallest reminder-surface truthfulness repair unless a direct Phase 11 build or replay file actually lands again on `master`.

## Non-Goals

This note does not widen Phase 11 into:

* a claim that the overall simple-driver tranche is closed
* a dedicated shared validator or replay stack beyond the landed reminder checkers and the still-parked Makefile plus workflow route markers
* broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, or khvcd execution
* a migration of driver-local reminder-note ownership into the shared packet
