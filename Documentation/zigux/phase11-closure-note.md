# Phase 11 Shared Closure Note

This note records the current bounded closure state for the active Phase 11 simple-driver tranche on `master`.

It does not claim that all of Phase 11 is complete. It closes only the shared review-surface gap around the packet that is already landed and parked:

- the watchdog starter lanes for `gpio_wdt`, `bcm2835_wdt`, and `dw_wdt`
- the bounded `hvc_console` starter and cleanup packet
- the focused shared UAPI header-boundary packet
- the shared build and make replay route that keeps those landed packets reviewable together

## Status

- `PHASE11_STATUS=parked`
- `PHASE11_CLOSURE_NOTE_STATUS=shared_packet_recorded`
- scope: active Phase 11 simple-driver tranche only
- shared replay route:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
  - `make -C zigux phase11`
- product boundary:
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  - `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-dw-wdt-survey.md`
  - `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-console-teardown-note.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `scripts/zigux/check-phase11-shared-replay-contract.py`
  - `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
  - `scripts/zigux/check-phase11-dw-wdt-packet.py`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `scripts/zigux/check-phase11-hvc-survey-packet.py`
  - `zigux/tests/phase11_build.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `zigux/tests/phase11_dw_wdt_manifest.json`
  - `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
  - `zigux/tests/phase11_dw_wdt_survey.zig`
  - `zigux/tests/phase11_hvc_cleanup.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/Makefile`

## What Is Already Landed

The current shared packet is already reviewable through one bounded route:

- `drivers/watchdog/gpio_wdt.zig` plus `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, its paired survey, and validation-matrix packet
- `drivers/watchdog/bcm2835_wdt.zig` plus `drivers/watchdog/bcm2835_wdt_verify.zig`, its manifest-backed survey, its validation matrix, and its dedicated archival checker route in `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig` plus `drivers/watchdog/dw_wdt_verify.zig`, its manifest-backed survey, its dedicated packet checker route in `scripts/zigux/check-phase11-dw-wdt-packet.py`, its registration-scaffold replay, its teardown note, and its validation matrix
- `drivers/tty/hvc/hvc_console.zig` plus `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_hvc_console_manifest.json`, its dedicated archival checker route in `scripts/zigux/check-phase11-hvc-survey-packet.py`, its checker-backed `make -C zigux phase11-hvc-survey` replay, its teardown note, and its validation matrix
- `Documentation/zigux/phase11-uapi-header-parity-survey.md` plus `zigux/tests/phase11_uapi_header_parity_manifest.json`, the focused `scripts/zigux/check-phase11-header-boundary-packet.py`, and the manifest-backed survey replay
- the shared contract and lane-sequencing notes that keep the shared-versus-driver-local split explicit

## What This Note Does Not Claim

This closure note does not claim:

- a shipped `validate-phase11.py`
- a shipped `make -C zigux phase11-validate` route
- a broader multi-checker validator stack beyond the current shared contract checker, dedicated bcm2835 packet checker, dedicated DesignWare packet checker, header-boundary checker, and HVC survey checker
- live tty teardown execution, notifier execution, or host-backed HVC cleanup
- platform-driver registration, PM base plumbing, clock or reset acquisition, live IRQ registration, or live MMIO validation for the watchdog starters
- any broader hardware-backed validation beyond the landed driver-local matrices and verify-backed replays

## Next Bounded Step

Keep the next follow-through inside the smallest truthful Phase 11 packet:

- first, reread `Documentation/zigux/review-checklist.md` and `scripts/zigux/check-phase11-shared-replay-contract.py` together, starting with the broad Phase 11 checklist question still naming the shared contract, the parked shared closure checkpoint, the focused header-boundary packet, and the dedicated HVC survey route without yet keeping the dedicated `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` and `scripts/zigux/check-phase11-dw-wdt-packet.py` archival routes explicit even though `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now do, so the next shared-surface repair stays inside that checklist-and-checker undercount rather than reopening already-aligned tests-root or scripts-root wording
- otherwise, take only a driver-local validation-matrix, teardown-note, survey, manifest, or registration-handoff sync inside one owning lane

Do not widen from this note into new driver behavior or a broader validator asset until those surfaces actually land on `master`.
