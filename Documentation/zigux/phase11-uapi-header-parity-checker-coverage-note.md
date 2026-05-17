# Phase 11 UAPI Header Parity Checker Coverage Note

## Status

- `PHASE11_UAPI_HEADER_CHECKER_COVERAGE_STATUS=checker_subset_gap_recorded`
- lane: `P11-L02`
- reviewed against current `master` on `2026-05-17`
- scope: record one bounded evidence step inside the shared Phase 11 UAPI header-boundary packet without reopening driver-local HVC or watchdog ownership

## Current Packet Evidence

The shared header-boundary packet on current `master` already carries broader evidence than the coupled deterministic checker currently enforces.

Current shared packet surfaces:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `drivers/tty/hvc/hvc_console.h`

Current manifest and survey evidence already include all of the following bounded proofs:
- `watchdog_info` layout assertions
- `winsize` layout assertions
- `hv_ops` callback-table layout assertions
- `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS`
- exported `hvc_console.h` helper declarations through `notifier_hangup_irq`

## Checker Coverage Gap

Current `master` still leaves one bounded checker-local gap inside `scripts/zigux/check-phase11-header-boundary-packet.py`.

The checker already fail-closes on:
- the shared lane key, phase, anchor, and roadmap destinations
- the older survey-summary subset through `watchdog_info`, `winsize`, and export-surface truthfulness
- the older manifest gap IDs through `phase11-build-gate`, the shared survey gate, the shared note, `phase11-dw-wdt-watchdog-info-layout-assert`, `phase11-hvc-console-winsize-layout-assert`, and `phase11-hvc-console-export-signature-assert`

The current manifest has moved further than that older checker subset. On current `master`, `zigux/tests/phase11_uapi_header_parity_manifest.json` also records:
- `hvc_hv_ops_layout_assert_present: true`
- `hvc_header_constants_checked: true`
- `phase11-hvc-console-hv-ops-layout-assert`
- `phase11-hvc-console-header-constant-assert`

Current `scripts/zigux/check-phase11-header-boundary-packet.py` does not yet require those two newer survey-summary booleans or those two newer manifest gap IDs as exact checker expectations. That means the shared checker still proves an older subset of the current packet even though the shared survey, manifest, matrix note, and `hvc_console.h` evidence have already widened inside the same bounded public-header surface.

## Why This Stays Bounded

- This note records a checker-local evidence gap only.
- It does not claim runtime notifier behavior, tty registration parity, khvcd execution, or watchdog-core integration.
- It does not reopen the dedicated HVC survey packet or any driver-local teardown lane.

## Next Bounded Step

The next honest same-packet follow-up is one checker-only tighten in `scripts/zigux/check-phase11-header-boundary-packet.py` so the shared checker also fails closed on:
- `hvc_hv_ops_layout_assert_present`
- `hvc_header_constants_checked`
- `phase11-hvc-console-hv-ops-layout-assert`
- `phase11-hvc-console-header-constant-assert`

That checker-only follow-up should stay scoped to the shared Phase 11 header-boundary packet and should not widen into new survey, manifest, or driver-local behavior claims.
