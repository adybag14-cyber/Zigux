# Phase 11 Fixture Refresh And Golden-Output Tooling Survey

This note records the remaining deterministic fixture-refresh and golden-output
tooling gap for the current shared Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_STATUS=deterministic_gap_open`
- lane: `P11-L07`
- reviewed against the current shared Phase 11 reminder packet
- scope: compare the surviving shared Phase 11 inventory and validation routes
  against the roadmap, keep the narrower HVC-only proof inventory honest, and
  record the missing deterministic fixture-refresh and golden-output tooling
  without reopening driver-local behavior or removed aggregate replay routes

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.
- A truthful shared deterministic tooling packet should help reviewers confirm
  fixture refreshes and expected-output evidence without overstating broader
  platform-backed closure.

## Current Repo Reality

- `make -C zigux phase11-validate` is the surviving shared Makefile route on
  current `master`.
- `scripts\zigux/validate_phase11.zig`,
  `scripts\zigux/check_phase11_build_inventory.zig`,
  `Documentation/zigux/phase11-shared-replay-contract.md`, and
  `Documentation/zigux/phase11-validation-matrix-gap-survey.md` are the shared
  reminder and checker surfaces that still describe the shipped Phase 11 packet.
- `zigux/tests/fixtures/phase11_build_inventory.json` truthfully records the
  narrower HVC current-head continuity packet, not a cross-driver replay roster.
- That shared build inventory currently carries 3 build test names, 0 shared
  `test_step.dependOn(...)` edges, 0 dedicated survey replays, 3 shared adjunct
  build replays, and 11 exact current checks.
- Current `master` does not materialize `make -C zigux phase11`,
  `make -C zigux phase11-contract`, or `zigux/tests/phase11_build.zig`.

## Deterministic Tooling Gap

- No shared Phase 11 fixture-refresh manifest currently records which simple
  driver fixtures were intentionally refreshed together and which were left
  driver-local.
- No shared Phase 11 golden-output checker or expectation catalog currently
  pins deterministic expected-output evidence across the surviving watchdog and
  HVC reminder packet.
- The returned HVC-focused build inventory is still useful, but it only proves a
  narrower current-head continuity slice and does not by itself cover cross-
  driver fixture refresh accounting or shared golden-output reviewability.

## Next Bounded Step

- Keep the next same-lane move shared-packet local: add one deterministic
  Phase 11 fixture-refresh manifest or one golden-output tooling checker that
  complements `phase11_build_inventory.json` without reviving removed aggregate
  replay routes.

## Review Rules

- Do not treat this survey as proof that broader shared Phase 11 replay routes
  already returned on current `master`.
- Do not widen this lane into gpio, bcm2835, DesignWare, HVC execution, or
  contributor-surface wording owned by neighboring Phase 11 lanes.
- If a later run lands a shared Phase 11 fixture-refresh or golden-output tool,
  refresh this note and its checker together in the same bounded pass.
