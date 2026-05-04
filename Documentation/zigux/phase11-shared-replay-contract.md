# Phase 11 Shared Replay Contract

This note records the current shared-versus-dedicated replay contract for the active Phase 11 simple-driver tranche on `master`.

It is intentionally review-first documentation. It does not claim a fresh local replay result; it captures the live packet shape already wired through the shared build, the committed inventory fixture, and the published validator-first route.

## Scope

- roadmap phase: `Phase 11: Simple Production Drivers`
- current bounded anchors: `drivers/watchdog/dw_wdt.c`, `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, and `drivers/tty/hvc/hvc_console.c`
- packet boundary: shared starter and split replay coverage stays inside `zigux/tests/phase11_build.zig`, while the archival `hvc_console` survey replay remains separate

## Pre-Replay Checker Stack

Run these in the published validator-first order before trusting the shared replay packet:

- `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase11-build-inventory.py`
- `python3 scripts/zigux/check-phase11-layout-assert-surface.py --self-test`
- `python3 scripts/zigux/check-phase11-layout-assert-surface.py`
- `python3 scripts/zigux/check-phase11-hvc-validation-flow.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-validation-flow.py`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
- `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`
- `python3 scripts/zigux/check-phase11-shared-replay-contract.py`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
- `python3 scripts/zigux/validate-phase11.py --self-test`
- `python3 scripts/zigux/validate-phase11.py`

The published wrapper remains `make -C zigux phase11-validate`.

The same contract is also exposed in bootstrap CI: `Validate Phase 11 header boundary packet` now runs before `Validate Phase 11 simple-driver bundle`, so the shared header-boundary packet must stay explicit before the broader Phase 11 delivery gate claims aligned evidence.

The same contract is fail-closed by `python3 scripts/zigux/check-phase11-shared-replay-contract.py` before the broader validator runs.

The broader validator follow-through stays intentionally smaller than the dedicated contract checker: today `scripts/zigux/validate-phase11.py` keeps the packet-wide manifest, docs, and shared replay alignment fail-closed, while `python3 scripts/zigux/check-phase11-shared-replay-contract.py` keeps the exact checklist-facing and shared-versus-dedicated replay wording fail-closed before that broader validator runs.

## Shared Replay Surface

The shared replay packet currently runs through these entrypoints:

- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

The current shared replay inventory explicitly keeps these focused split and adjunct replays inside that shared Phase 11 packet:

- `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`

Those shared replay markers are the same ones tracked in `zigux/tests/fixtures/phase11_build_inventory.json` and checked by `scripts/zigux/check-phase11-build-inventory.py`.

## Dedicated Boundary

The dedicated archival replay remains separate from the shared build packet:

- `make -C zigux phase11-hvc-survey`
- `zigux/tests/phase11_hvc_console_survey.zig`

That boundary is intentional. The shared packet should keep the exact shared replay inventory explicit without silently implying that every `hvc_console` survey gate already runs inside `zigux/tests/phase11_build.zig`.

The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:

- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

That packet should remain reviewable as a shared header-boundary check before the broader Phase 11 bundle claims aligned evidence.

## Contributor Sync Points

When the shared-versus-dedicated replay contract changes, keep these contributor-facing guidance surfaces aligned with this note:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those surfaces are where contributors usually discover the Phase 11 route before they open the deeper packet notes, so any replay-contract change should stay explicit there as well.

The four driver-local validation matrices belong in that same sync set because each roadmap-backed driver lane names the shared Phase 11 replay route there; if the shared replay contract changes without those matrix notes moving too, the contributor-facing matrix packet starts undercounting the live simple-driver tranche.

In particular, the `zigux/tests/README.md` Phase 11 guidance now repeats the four shared split and adjunct replays, the four driver-local manifests, and `scripts/zigux/check-phase11-header-boundary-packet.py` explicitly, so the tests-root carryover prompt matches the shared contract note, the validator-first guide, and the tests-root review companion.

The same four driver-local manifests should stay explicit in `Documentation/zigux/README.md` whenever the docs-root Phase 11 summary is refreshed, so the top-level docs index does not undercount the active simple-driver packet while the tests-root and checklist-facing prompts stay precise.

## Review Use

Use this note when a simple-driver change touches the shared Phase 11 test packet, the pre-replay checker stack, or the split replay inventory.

The minimum agreement surface for that kind of change is:

- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-layout-assert-surface.py`
- `scripts/zigux/check-phase11-hvc-validation-flow.py`
- `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/validate-phase11.py`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

If those files drift apart, the Phase 11 delivery packet stops being reviewable even if individual Zig test files still look plausible in isolation.
