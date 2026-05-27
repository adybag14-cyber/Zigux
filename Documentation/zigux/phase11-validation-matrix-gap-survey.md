# Phase 11 Validation Matrix Gap Survey

This note records roadmap-facing validation-matrix coverage and the current deterministic fixture and golden-output tooling gap for the shared Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- shared packet lane: `P11-Y06`
- deterministic tooling survey lane: `P11-L07`
- reviewed against live `master`
- scope: keep the returned driver-local matrix roster explicit, keep the shared Phase 11 build-proof fan-out honest, and record the current deterministic fixture and golden-output tooling gap without widening into driver-local execution claims

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.
- The roadmap expectation is stronger than build presence alone: the shared packet should stay machine-reviewable when fixture inventories move and when teardown-or-failure-mode proof routes refresh.

## Current Repo Reality

Authenticated GitHub contents rereads in this run rematerialize the bcm2835, gpio watchdog, HVC console, and DesignWare driver-local Phase 11 matrix notes named by the roadmap on current `master`.

The currently reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap.

`zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `zigux/tests/phase11_dw_wdt_manifest.json` are the current machine-readable deterministic fixture surfaces inside the shared Phase 11 packet.

The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.

`zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `zigux/tests/phase11_dw_wdt_restart_build.zig`, and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` are the current focused teardown-or-failure-mode proof builds directly named by the shared packet.

`make -C zigux phase11-validate` remains the returned shared validation route, and `scripts/zigux/validate-phase11.py` keeps the current shared packet build-proof-first.

The same narrower inventory also records 3 adjunct build replays through `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`.

The same narrower continuity packet also stays `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`.

The directly readable HVC current-head packet also now includes `zigux/tests/phase11_hvc_modem_control_proof.zig`, `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness, and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard.

The same directly readable HVC current-head packet also keeps `Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`, `scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`, `zigux/tests/phase11_hvc_current_head_manifest.json`, and `scripts/zigux/check-phase11-hvc-current-head-manifest.py` explicit so the cleanup-trigger split and machine-readable packet roster stay reviewable beside those focused HVC failure-mode builds.

The same narrower continuity packet also keeps the dedicated `scripts/zigux/check-phase11-hvc-cleanup-current-head.py` guard explicit through `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`.

The same narrower continuity packet also keeps the dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard explicit through `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`.

The same narrower continuity packet now also records 2 focused direct build checker routes through `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test` and `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`, together with 2 focused direct build replays through `zigux/tests/phase11_hvc_modem_control_proof_build.zig` and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`.

The shared current-head packet also now keeps `zigux/tests/phase11_dw_wdt_restart_build.zig` and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` directly readable beside the returned driver-local matrices, so the watchdog teardown-or-failure-mode proof pair stays explicit even while the narrower shared inventory remains HVC-centered.

The shared `phase11-validate` route also now carries `zigux/tests/phase11_hvc_modem_control_proof_build.zig` as a focused HVC teardown-or-failure-mode proof outside the narrower three-entry build inventory.

The shared `phase11-validate` route also now carries `zigux/tests/phase11_dw_wdt_restart_build.zig` and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` as focused watchdog teardown-or-failure-mode proofs outside the narrower three-entry HVC build inventory, so keep those shared watchdog replay routes explicit beside the returned driver-local matrices instead of reducing the shared gate to HVC-only proof coverage.

Current `master` also materializes `scripts/zigux/validate-phase11.py` and `zigux/Makefile`, and the live Makefile exposes `make -C zigux phase11-validate`.

`bcm2835_wdt`: authenticated GitHub contents rereads now rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`.

The returned bcm2835 matrix also keeps its bounded timeout, probe-summary ownership, runtime register modeling, restart-or-poweroff intent, and teardown-note packet explicit instead of reducing the bcm2835 lane to a presence-only roster entry while leaving bcm2835-only reminder wording, replay claims, and platform-backed execution in the bcm2835 owner lane.

`gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly readable on current `master`, and it keeps the bounded descriptor, platform-drvdata, teardown, registration-handoff, register-device request, and failure-mode parity review packet explicit without claiming live GPIO descriptor execution or platform registration.

`dw_wdt`: authenticated GitHub contents rereads now rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

## Deterministic Tooling Gap

The shared Phase 11 packet now rematerializes a dedicated golden-output fixture roster through `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check-phase11-validate-check-roster.py` and `scripts/zigux/check-phase11-validate-route-alignment.py` guards.

It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.

`scripts/zigux/validate-phase11.py` and `make -C zigux phase11-validate` therefore stay build-proof-first rather than expected-output-refresh-first.

The current machine-readable fixtures now capture route inventory, validate-check coverage, and manifest coverage, but they still do not refresh or compare stable expected-output artifacts for the shared Phase 11 proof fan-out.

That leaves a narrower roadmap-facing deterministic tooling gap: the repo can prove that the focused builds still compile and run, and it can exact-check the shared validate roster, but it still cannot refresh and diff shared golden outputs for the same bounded packet.

## Review Rules

- Treat this survey as current-head matrix and deterministic-tooling truthfulness only, not as proof of platform-backed closure.
- Keep the returned four-matrix packet explicit through bcm2835, gpio, HVC, and DesignWare rereads while leaving bcm2835-only, gpio-only, DesignWare-only, and HVC-only behavior claims in their owner lanes.
- Keep the machine-readable deterministic packet explicit through `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `zigux/tests/phase11_dw_wdt_manifest.json`.
- Keep the focused teardown-or-failure-mode proof builds explicit through `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `zigux/tests/phase11_dw_wdt_restart_build.zig`, and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` rather than silently collapsing them into the narrower three-entry HVC inventory.
- Do not claim that golden-output refresh tooling already exists just because the shared validate route and focused proof builds returned.
- If a dedicated refresh helper route or artifact-diff guard lands later, update this survey, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `scripts/zigux/check-phase11-validation-matrix-gap-survey.py` in the same bounded pass.
