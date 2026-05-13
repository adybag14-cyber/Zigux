# Phase 11 UAPI Header Parity Survey

## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored`
- `surveyed_commit=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- lane: `P11-L18`
- scope: keep the maintained shared UAPI header parity packet reviewable for `watchdog_info`, `winsize`, the `hv_ops` callback table, and the exported `hvc_console.h` constants and helper declarations without widening into tty-core or watchdog core ownership

## Current Repo Reality

- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_build.zig`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `drivers/tty/hvc/hvc_console.h`

## Boundary Packet

- `phase11-build-gate`: the shared Phase 11 build route includes `phase11-uapi-header-parity-survey-tests` again.
- `phase11-uapi-header-parity-surface`: the shared survey remains the paired UAPI header parity packet for the public header boundary.
- `phase11-dw-wdt-watchdog-header-boundary`: `struct watchdog_info` remains the bounded public watchdog header checkpoint.
- `phase11-dw-wdt-watchdog-info-layout-assert`: size `40`, alignment `4`, field offsets `0`, `4`, and `8`.
- `phase11-hvc-console-winsize-layout-assert`: `struct winsize` remains size `8`, alignment `2`, with field offsets `0`, `2`, `4`, and `6`.
- `phase11-hvc-console-hv-ops-layout-assert`: `struct hv_ops` remains size `72`, alignment `8`, with callback-table offsets `0` through `64`.
- `phase11-hvc-console-header-constant-assert`: the shared survey checks `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` in `drivers/tty/hvc/hvc_console.h`.
- `phase11-hvc-console-export-signature-assert`: the shared survey checks the exact exported `hvc_instantiate`, `hvc_alloc`, `hvc_remove`, `hvc_poll`, `hvc_kick`, `__hvc_resize`, `notifier_add_irq`, `notifier_del_irq`, and `notifier_hangup_irq` declarations in `drivers/tty/hvc/hvc_console.h`.

## Shared Versus Dedicated Replay

- shared replay path: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- wider Phase 11 replay route: `make -C zigux phase11`
- `scripts/zigux/check-phase11-header-boundary-packet.py` remains the fail-closed deterministic checker for this shared public-surface packet, so follow-through here should stay inside the header-boundary evidence instead of drifting into broader contributor-facing reminder wording.
- `Documentation/zigux/phase11-driver-lane-sequencing.md` keeps the parked owner-map split explicit so this shared header packet stays outside the bcm2835, GPIO, DesignWare, and HVC driver-local lanes even when those lanes cite the shared UAPI boundary.
- `Documentation/zigux/phase11-closure-note.md` keeps the parked shared closure checkpoint explicit so this survey stays tied to the same bounded Phase 11 packet as the wider build-and-make route.
- the dedicated HVC note, teardown companion, and validation matrix remain separate documentation because `zigux/tests/phase11_hvc_console_survey.zig` still reads the broader driver-local note packet and notifier-facing matrix, `zigux/tests/phase11_hvc_console_manifest.json` keeps the archival HVC landing checkpoint explicit, `Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps the dedicated teardown companion explicit, and that survey replay stays on the dedicated `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` step plus the fail-closed `scripts/zigux/check-phase11-hvc-survey-packet.py` and `make -C zigux phase11-hvc-survey` route inside the same `phase11_build.zig` file on `master` rather than the shared `test` step

## Why This Stays Bounded

- The shared packet proves only public header layouts, constants, and exported helper declaration truthfulness.
- It does not claim tty registration parity, notifier execution, khvcd worker execution, live sysrq dispatch, or watchdog core integration.
- Any new driver-local handoff belongs in the dedicated `hvc_console` or watchdog lanes instead of widening this shared packet.
