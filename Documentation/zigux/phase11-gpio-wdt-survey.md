# Phase 11 gpio_wdt Survey

## Scope

- Lane: `P11-L01`
- Roadmap phase: `Phase 11: Simple Production Drivers`
- Linux anchor: `drivers/watchdog/gpio_wdt.c`
- Recommended Zigux destination: `drivers/watchdog/gpio_wdt.zig`

## Current repo state

- The live branch still contains the Linux `gpio_wdt.c` implementation but no `drivers/watchdog/gpio_wdt.zig`.
- The live Zigux tree also had no dedicated `phase11_build.zig`, gpio_wdt survey manifest, or Phase 11 note before this lane.
- This run keeps the work survey-only so the simple-driver gap is explicit and reviewable without pretending watchdog parity already exists.

## Bounded gap

- `gpio_wdt.c` carries a small but real hardware-facing lifecycle: property parsing for `hw_algo`, `hw_margin_ms`, and `always-running`; GPIO acquisition; ping semantics for toggle versus level mode; and watchdog start or stop state updates.
- Zigux does not yet model those state transitions in a bounded, in-memory driver scaffold.
- The next honest step is a narrow `drivers/watchdog/gpio_wdt.zig` starter that captures configuration validation and start, stop, or ping bookkeeping before any broader hardware validation matrix work.

## Validation added here

- `zigux/tests/phase11_gpio_wdt_manifest.json` records the current gap and the next bounded step.
- `zigux/tests/phase11_gpio_wdt_survey.zig` checks that the manifest still describes the repo honestly.
- `zigux/tests/phase11_build.zig` and `make -C zigux phase11` provide a dedicated Phase 11 survey gate.
