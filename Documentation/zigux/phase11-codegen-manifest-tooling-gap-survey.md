# Phase 11 Codegen and Manifest Tooling Gap Survey

This note records the current deterministic tooling posture for the shared Phase 11 simple-driver packet and names the smallest roadmap-aligned manifest or generated-summary follow-through that still remains on current `master`.

## Status

- `PHASE11_TOOLING_GAP_STATUS=shared_packet_aggregate_surface_materialized`
- lane: `P11-L04`
- scope: keep the shared Phase 11 codegen-and-manifest tooling story honest without widening into driver-local behavior, broader reminder-surface ownership, or retired aggregate routes

## Roadmap Anchor

Phase 11 still exists to move from lab-only slices toward bounded simple production drivers.
The roadmap still requires:

- direct-port or dual-implementation driver templates
- a hardware validation matrix
- teardown and failure-mode parity

For the shared tooling packet, that means current reminder surfaces, machine-readable manifests, and proof routes must stay deterministic without reviving retired wrappers or pretending a narrow inventory already describes the whole surviving Phase 11 packet.

## Current Shared Deterministic Tooling Packet

Current shared Phase 11 tooling evidence on `master` now centers on the returned validator-and-proof packet:

- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md`
- `Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-validate-manifest-roster.py`
- `scripts/zigux/check-phase11-validate-check-roster.py`
- `scripts/zigux/check-phase11-validate-route-alignment.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-shared-replay-contract-counts.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-hvc-current-head-manifest.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/check-phase11-dw-wdt-build-route.py`
- `scripts/zigux/check-phase11-shared-tooling-manifest.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json`
- `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`
- `zigux/tests/fixtures/phase11_validate_checks.json`
- `zigux/Makefile`
- `make -C zigux phase11-validate`

That shared packet is stronger than the older replay-only story: `scripts/zigux/validate-phase11.py` exists, `make -C zigux phase11-validate` is the live shared route, and the aggregate manifest now records the shared checker stack and proof fan-out without pretending it replaces the narrower HVC continuity inventory.
`scripts/zigux/check-phase11-shared-tooling-manifest.py` is already wired into `scripts/zigux/validate-phase11.py`, and `zigux/tests/fixtures/phase11_validate_checks.json` records both the shared tooling-manifest self-test and live validator entries.
The aggregate surface now also carries the shared watchdog lifecycle note plus the cleanup-prerequisite and current-head manifest guards that the validator route already ships.
The same current validator fixture also records the DesignWare build-route guard and its `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json` fixture.

The exact deterministic command set recorded by the current shared validator fixture is:

- `python3 scripts/zigux/validate-phase11.py --self-test`
- `python3 scripts/zigux/check-phase11-validate-manifest-roster.py --self-test`
- `python3 scripts/zigux/check-phase11-validate-manifest-roster.py`
- `python3 scripts/zigux/check-phase11-validate-check-roster.py --self-test`
- `python3 scripts/zigux/check-phase11-validate-check-roster.py`
- `python3 scripts/zigux/check-phase11-validate-route-alignment.py --self-test`
- `python3 scripts/zigux/check-phase11-validate-route-alignment.py`
- `python3 scripts/zigux/check-phase11-shared-tooling-manifest.py --self-test`
- `python3 scripts/zigux/check-phase11-shared-tooling-manifest.py`
- `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase11-build-inventory.py`
- `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`
- `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `python3 scripts/zigux/check-phase11-shared-replay-contract-counts.py --self-test`
- `python3 scripts/zigux/check-phase11-shared-replay-contract-counts.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py --self-test`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py --self-test`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py --self-test`
- `python3 scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`
- `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py --self-test`
- `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-build-route.py --self-test`
- `python3 scripts/zigux/check-phase11-dw-wdt-build-route.py`
- `zig build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
- `zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig`
- `zig build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig`
- `zig build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

Use `python3 scripts/zigux/validate-phase11.py --skip-zig-builds` when a scheduled environment cannot expose the pinned Zig toolchain or a runnable checkout; that still verifies the Python checker chain and records the skipped Zig proof-build count.

## Live Gap Versus The Roadmap

The narrower shared manifest gap recorded earlier is now materially closed.

Current `master` now ships a small aggregate surface through:

- `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`
- `scripts/zigux/check-phase11-shared-tooling-manifest.py`

That aggregate surface enumerates the live shared checker stack, the surviving shared validation routes, the allowed driver-local matrix notes, and the focused proof-backed build shards that the shared packet is still allowed to name.
It distinguishes the narrower `zigux/tests/fixtures/phase11_build_inventory.json` HVC continuity packet from the broader shared `phase11-validate` checker stack and proof fan-out, so reminder notes no longer need to overload one HVC-only inventory as if it covered the entire shared Phase 11 packet.

## Boundaries For Follow-Through

Keep the next deterministic-tooling step narrow:

- do not revive removed `phase11`, `phase11-contract`, or `zigux/tests/phase11_build.zig` routes just to recover old naming
- do not collapse bcm2835, gpio, DesignWare, HVC, and header-boundary evidence into one fake green dashboard
- do not widen this tooling step into driver behavior, platform-backed execution, or broader contributor-surface ownership already handled by nearby Phase 11 lanes
- do not treat the narrower `zigux/tests/fixtures/phase11_build_inventory.json` packet as if it already covers the whole shared validator route

## Recommended Next Bounded Step

The next bounded follow-through can stay smaller:

- reread the broader shared reminder summaries against `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, `scripts/zigux/validate-phase11.py`, and `zigux/tests/fixtures/phase11_validate_checks.json` before widening any shared Phase 11 aggregate wording
- keep the aggregate manifest limited to shared tooling surfaces and explicitly allowed proof-backed build shards
- update broader reminder summaries only after that reread confirms the shared validator packet still matches current-head repo reality
