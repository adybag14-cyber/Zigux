# Phase 11 DesignWare Watchdog Provenance Readback

This note records one bounded truthfulness gap in the current Phase 11 `dw_wdt` packet on `master`.

## Live Readback
- `zigux/tests/phase11_dw_wdt_manifest.json` currently pins the DesignWare watchdog packet to lane `P11-L10` at surveyed commit `6726fdd9da4eef55498fb06c38815317a684bcbf`.
- `Documentation/zigux/phase11-dw-wdt-survey.md` still says the packet was reread at `75f8336c4305beed127d7abfae37d3999b7cc57c` and still says the cleanup packet carries lane identity `P11-L05`.
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` still reports the same older surveyed packet pin `75f8336c4305beed127d7abfae37d3999b7cc57c` and the same older continuity `P11-L05`.

## Why This Matters
- The current DesignWare watchdog packet is still substantively useful: the bounded driver starter, teardown and failure-mode verify replay, registration scaffold replay, survey gate, and shared replay route all remain present on `master`.
- The live mismatch is provenance drift, not a missing helper or missing teardown packet.
- Leaving the drift undocumented makes later note refreshes harder to scope because the manifest-backed packet identity and the docs-root packet identity no longer agree.

## Bounded Next Step
- Sync `Documentation/zigux/phase11-dw-wdt-survey.md` and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` to the manifest-backed lane key `P11-L10` and surveyed commit `6726fdd9da4eef55498fb06c38815317a684bcbf`.
- Keep that repair documentation-only.
- Do not widen into platform registration, PM, IRQ wiring, reset acquisition, debugfs support, or live MMIO behavior while closing this provenance gap.
