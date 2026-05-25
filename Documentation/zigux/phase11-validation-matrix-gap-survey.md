# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- lane: `P11-Y06`
- reviewed against live `master`
- scope: verify the current driver-local matrix packet against the roadmap,
  keep the authenticated-contents reread boundary honest, and record the
  current roadmap-visible matrix roster without widening into driver-local
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
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- `zigux/tests/phase11_dw_wdt_restart_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`

Authenticated GitHub contents rereads in this run rematerialize the bcm2835,
gpio watchdog, HVC console, and DesignWare driver-local Phase 11 matrix notes
named by the roadmap on current `master`.

The currently reread driver-local Phase 11 matrix notes on current `master` are
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
useful adjacent shared evidence, but it is not one of the driver-local Phase 11
validation matrices named by the roadmap.

`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower
current-head HVC continuity packet.

The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared
depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.
That inventory does not stand in for a whole-Phase-11 replay roster while the
shared survey keeps the returned four-matrix packet explicit.
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
The directly readable HVC current-head packet also now includes
`zigux/tests/phase11_hvc_modem_control_proof.zig`,
`zigux/tests/phase11_hvc_modem_control_proof_build.zig`, the standalone
`zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness, and
`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard, so
keep that modem-control and targetless-unregister failure-mode evidence explicit
beside the narrower three-proof inventory instead of silently collapsing it into
the shared proof-backed roster.
The same narrower continuity packet also keeps the dedicated
`scripts/zigux/check-phase11-hvc-cleanup-current-head.py` guard explicit
through
`python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test`
and `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, so keep
that focused cleanup-current-head route explicit beside the narrower HVC proof
packet instead of treating the cleanup companion evidence as unchecked prose.
The same narrower continuity packet also keeps the dedicated
`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard
explicit through
`python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test`
and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
so keep that focused witness-check route explicit beside the standalone witness
pair instead of treating the pair as unchecked prose evidence.
The same narrower continuity packet now also records 2 focused direct build
checker routes through
`python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`
and `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`,
together with 2 focused direct build replays through
`zigux/tests/phase11_hvc_modem_control_proof_build.zig` and
`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`.
The shared current-head packet also now keeps
`zigux/tests/phase11_dw_wdt_restart_build.zig` and
`zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` directly
readable beside the returned driver-local matrices, so the watchdog teardown-or-
failure-mode proof pair stays explicit even while the narrower shared inventory
remains HVC-centered.
The shared `phase11-validate` route also now carries
`zigux/tests/phase11_hvc_modem_control_proof_build.zig` as a focused HVC
teardown-or-failure-mode proof outside the narrower three-entry build
inventory, so keep that direct replay route explicit beside the modem-control
note pair instead of silently collapsing it into the shared inventory-backed
roster.
The shared `phase11-validate` route also now carries
`zigux/tests/phase11_dw_wdt_restart_build.zig` and
`zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` as focused
watchdog teardown-or-failure-mode proofs outside the narrower three-entry HVC
build inventory, so keep those shared watchdog replay routes explicit beside the
returned driver-local matrices instead of reducing the shared gate to HVC-only
proof coverage.
That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap
on current `master`: the repo does not yet rematerialize a broader shared
replay or survey route that would carry cross-driver public-struct ABI proof
beyond those surviving `layout_assert` shards.

Current `master` also materializes `scripts/zigux/validate-phase11.py` and
`zigux/Makefile`, and the live Makefile exposes `make -C zigux phase11-validate`,
so keep that returned shared validation-and-build gate explicit beside the
matrix packet without treating route presence as proof of full platform-backed
closure.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `python3 scripts/zigux/validate-phase11.py`

## Matrix Survey

- `bcm2835_wdt`: authenticated GitHub contents rereads now rematerialize
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so keep that
  returned roadmap-required bcm2835 driver-local matrix explicit. The returned
  bcm2835 matrix also keeps its bounded timeout, probe-summary ownership,
  runtime register modeling, restart-or-poweroff intent, and teardown-note
  packet explicit instead of reducing the bcm2835 lane to a presence-only roster
  entry while leaving bcm2835-only reminder wording, replay claims, and
  platform-backed execution in the bcm2835 owner lane.
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
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py` route also stays
  directly readable beside that smaller proof inventory and cleanup companion
  packet.
  The dedicated
  `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` route also
  stays directly readable beside that smaller proof inventory and standalone
  witness pair.
  The dedicated
  `scripts/zigux/check-phase11-focused-direct-build-replays.py` route also now
  stays directly readable beside the modem-control and targetless-unregister
  build pair, so the focused direct replay packet is checker-backed instead of
  prose-only.
  The shared `phase11-validate` route likewise keeps
  `zigux/tests/phase11_hvc_modem_control_proof_build.zig` explicit as a
  focused modem-control teardown-or-failure-mode proof outside the narrower
  three-entry build inventory.
- `dw_wdt`: authenticated GitHub contents rereads now rematerialize
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so keep that
  returned roadmap-required DesignWare driver-local matrix explicit. The
  returned DesignWare matrix also keeps its reset-controlled versus
  continued-heartbeat teardown split, idle remove-time heartbeat preservation,
  and registration-facing handoff review packet explicit instead of reducing
  the DesignWare lane to a presence-only roster entry while leaving
  DesignWare-local reminder wording, continuity claims, and platform-backed
  execution in the DesignWare owner lane.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the reread bcm2835, gpio, HVC, or DesignWare matrices, the
  adjacent header-parity matrix, the narrower HVC continuity packet, the
  standalone targetless-unregister witness, or the returned shared
  validation-and-build gate to overclaim broader GPIO descriptor execution,
  watchdog-core registration side effects, notifier execution, khvcd execution,
  sysrq execution, MMIO behavior, or host-backed teardown.
- Keep the returned four-matrix driver-local packet explicit through bcm2835,
  gpio, HVC, and DesignWare contents rereads while preserving the roadmap-
  required teardown or failure-mode cues each returned matrix already carries,
  rather than reducing bcm2835 or DesignWare to presence-only roster entries.
- Keep bcm2835-only and DesignWare-only reminder follow-through in their owner
  lanes even though both roadmap-required matrices now reread through
  authenticated GitHub contents.
- Keep the roadmap-facing ABI proof gap explicit until current `master`
  rematerializes a broader shared replay or survey route that carries
  cross-driver public-struct ABI proof beyond the surviving HVC-centered
  `layout_assert` shards.
- If a driver-local matrix returns or disappears, update this survey and both
  matrix-gap checkers in the same bounded pass so the shared packet description
  stays honest.
