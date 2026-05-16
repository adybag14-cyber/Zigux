# Phase 11 DesignWare Watchdog Clock-Acquisition Plan

This note narrows the next `drivers/watchdog/dw_wdt.zig` step to the first real platform-backed call surface after the already-landed starter, lifecycle, scaffold, and verification packet.

## Current Packet Boundary

- `dw_wdt.zig` already keeps timeout-window setup, probe-time bookkeeping, platform-resource preflight, registration-facing handoff, platform-registration scaffold anchors, stop summaries, teardown summaries, and remove summaries reviewable without claiming live platform execution.
- `dw_wdt_verify.zig` already replays missing-`drvdata` registration blockers, shared-clock fallback handoff, continued-heartbeat teardown and remove paths when reset control is absent, and reset-backed cleanup when reset control is present.
- `zigux/tests/phase11_dw_wdt.zig` already keeps the named-`tclk`, shared-clock fallback, and blocked-no-clock preflight cases explicit.
- The live validation matrix already points the next substantive DesignWare move at one real probe or remove execution slice with matching validation evidence instead of more note-only churn.

## Chosen Next Slice

Land only the timer-clock acquisition step in the probe path.

- model the first live `devm_clk_get_enabled()` call for a named `tclk`
- preserve the existing shared-clock fallback when the named timer clock is absent
- keep the driver blocked before watchdog registration when neither timer-clock path is available
- keep the handoff explicitly pre-registration, pre-reset-acquisition, pre-IRQ, and pre-MMIO

## Non-Goals

- no APB clock acquisition in this slice
- no reset-control acquisition or release
- no IRQ registration
- no `watchdog_register_device` execution
- no PM, debugfs, suspend or resume, remove or shutdown, or hardware-backed validation claims

## Required Code Touch Points

- `drivers/watchdog/dw_wdt.zig`: add one small driver-backed helper that records named-`tclk` success, shared-clock fallback success, and blocked-no-clock failure as the first live platform-resource call surface
- `drivers/watchdog/dw_wdt_verify.zig`: replay the helper against those three acquisition outcomes without widening into reset, IRQ, or watchdog-core registration
- `zigux/tests/phase11_dw_wdt.zig`: keep the narrow preflight expectations aligned with the new acquisition helper
- directly coupled survey or matrix wording only after the code lands, and only where the existing packet would otherwise overclaim or drift

## Validation Gate

- run focused Zig validation on the exact `dw_wdt.zig` and `dw_wdt_verify.zig` surface after the final edit
- keep the existing focused `phase11_dw_wdt.zig` replay green
- update shared packet checks only if the new helper changes their current explicit markers
- do not publish any Zig change if the focused Zig validation reports an error

## Exit Criteria

- one driver-backed helper exists for timer-clock acquisition only
- verification covers named-`tclk` success, shared fallback success, and blocked-no-clock failure
- the packet still refuses to claim reset ownership, IRQ ownership, watchdog-core registration, PM, debugfs, or live MMIO execution
