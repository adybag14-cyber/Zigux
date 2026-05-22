# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_roster_incomplete_on_current_master`
- lane: `P11-L01`
- reviewed against live `master`
- scope: verify the current driver-local matrix packet against the roadmap,
  keep the authenticated-contents boundary honest, and record the current
  roadmap-visible matrix roster gap without widening into driver-local
  implementation or platform-backed execution

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

Current direct contents reads in this run rematerialize the gpio watchdog and
HVC console driver-local Phase 11 matrix notes named by the roadmap, but they
do not rematerialize the bcm2835 or DesignWare driver-local matrix notes on
current `master`.

The directly readable driver-local Phase 11 matrix notes on current `master`
are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`.

Current direct contents reads in this run do not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
useful adjacent shared evidence, but it is not one of the driver-local Phase 11
validation matrices named by the roadmap.

`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower
current-head HVC continuity packet.

The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared
depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.
That inventory does not stand in for a whole-Phase-11 replay roster while the
current reread matrix roster remains incomplete.
The same narrower inventory also records 3 adjunct build replays through
`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
`zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and
`zigux/tests/phase11_hvc_cleanup_packet_build.zig`, so keep those current-head
HVC build routes explicit as adjacent continuity evidence rather than treating
them as a cross-driver replay roster.
The same narrower continuity packet also stays `layout_assert`-backed through
`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and
`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, so keep those
surviving ABI proof shards explicit as adjacent HVC continuity evidence instead
of treating the three build routes as prose-only review support.
The directly readable HVC current-head packet also now includes the standalone
`zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and
`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard, so
keep that targetless-unregister failure-mode evidence explicit beside the
narrower three-proof inventory instead of silently collapsing it into the shared
proof-backed roster.
The same narrower continuity packet also keeps the dedicated
`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard
explicit through
`python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test`
and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
so keep that focused witness-check route explicit beside the standalone witness
pair instead of treating the pair as unchecked prose evidence.
That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap
on current `master`: the repo does not yet rematerialize a broader shared
replay or survey route that would carry cross-driver public-struct ABI proof
beyond those surviving `layout_assert` shards.

Current `master` also materializes `scripts/zigux/validate-phase11.py` and
`zigux/Makefile`, and the live Makefile exposes `make -C zigux phase11-validate`,
so keep that returned shared validation-and-build gate explicit beside the
matrix packet without treating route presence as proof that the driver-local
matrix roster is complete.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `python3 scripts/zigux/validate-phase11.py`

## Matrix Survey

- `bcm2835_wdt`: current direct contents reads do not rematerialize
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so the
  roadmap-required bcm2835 driver-local matrix remains an open packet gap on
  current `master`; keep the next repair in the bcm2835 owner lane rather than
  widening this shared survey into bcm2835-local reminder wording, replay
  claims, or platform-backed execution.
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is
  directly readable on current `master`, and it keeps the bounded descriptor,
  platform-drvdata, teardown, registration-handoff, register-device request,
  and failure-mode parity review packet explicit without claiming live GPIO
  descriptor execution or platform registration.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  is directly readable on current `master`, and the narrower build inventory now
  keeps the HVC current-head continuity packet explicit through
  `phase11-hvc-hv-ops-layout-proof-tests`,
  `phase11-hvc-export-surface-layout-proof-tests`, and
  `phase11-hvc-cleanup-packet-proof`.
  Those surviving proof tests still hang off the `layout_assert`-backed
  `hv_ops` and exported-surface proof shards rather than a broader shared ABI
  replay.
  The standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
  witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
  build shard also stay directly readable beside that smaller proof inventory.
  The dedicated
  `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` route also
  stays directly readable beside that smaller proof inventory and standalone
  witness pair.
- `dw_wdt`: current direct contents reads do not rematerialize
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the
  roadmap-required DesignWare driver-local matrix remains an open packet gap on
  current `master`; keep the next repair in the DesignWare owner lane instead
  of widening this shared survey into DesignWare-local reminder wording,
  continuity claims, or platform-backed execution.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the directly readable gpio and HVC matrices, the adjacent
  header-parity matrix, the narrower HVC continuity packet, the standalone
  targetless-unregister witness, or the returned shared validation-and-build
  gate to overclaim broader GPIO descriptor execution, watchdog-core
  registration side effects, notifier execution, khvcd execution, sysrq
  execution, MMIO behavior, or host-backed teardown.
- Keep the directly readable driver-local matrix packet explicit through gpio
  and HVC contents reads while preserving the narrower HVC build inventory, its
  adjunct build routes, the surviving `layout_assert`-backed ABI proof shards,
  the dedicated targetless-unregister witness checker route, and the standalone
  targetless-unregister witness as adjacent continuity evidence rather than a
  cross-driver replay roster.
- Keep the roadmap-facing matrix gap explicit until current `master`
  rematerializes the missing bcm2835 and DesignWare driver-local matrix notes.
- Keep the roadmap-facing ABI proof gap explicit until current `master`
  rematerializes a broader shared replay or survey route that carries
  cross-driver public-struct ABI proof beyond the surviving HVC-centered
  `layout_assert` shards.
- If a driver-local matrix returns or disappears, update this survey and both
  matrix-gap checkers in the same bounded pass so the shared packet description
  stays honest.
