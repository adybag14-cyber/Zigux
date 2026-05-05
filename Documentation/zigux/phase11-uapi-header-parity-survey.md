# Phase 11 UAPI Header Parity Survey

## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored`
- `surveyed_commit=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- lane: `P11-L08`
- scope: restore the paired UAPI header parity packet that keeps the public `watchdog_info`, `winsize`, and exported `hvc_*` helper surface reviewable without widening into tty-core or watchdog core ownership

## Current Repo Reality

- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_build.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `drivers/tty/hvc/hvc_console.zig`

## Boundary Packet

- `phase11-build-gate`: the shared Phase 11 build route includes `phase11-uapi-header-parity-survey-tests` again.
- `phase11-uapi-header-parity-surface`: the shared survey remains the paired UAPI header parity packet for the public header boundary.
- `phase11-dw-wdt-watchdog-header-boundary`: `struct watchdog_info` remains the bounded public watchdog header checkpoint.
- `phase11-dw-wdt-watchdog-info-layout-assert`: size `40`, alignment `4`, field offsets `0`, `4`, and `8`.
- `phase11-hvc-console-winsize-layout-assert`: `struct winsize` remains size `8`, alignment `2`, with field offsets `0`, `2`, `4`, and `6`.
- `phase11-hvc-console-export-signature-assert`: the shared survey checks the exported `hvc_instantiate`, `hvc_alloc`, `hvc_remove`, `hvc_poll`, `hvc_kick`, `__hvc_resize`, `notifier_add_irq`, and `notifier_del_irq` surface.

## Shared Versus Dedicated Replay

- shared replay path: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- wider Phase 11 replay route: `make -C zigux phase11`
- the dedicated HVC note and validation matrix remain separate documentation because `zigux/tests/phase11_hvc_console_survey.zig` still reads the broader driver-local note packet and notifier-facing matrix, but that survey replay now runs inside the same shared `phase11_build.zig` route on `master`

## Why This Stays Bounded

- The shared packet proves only public header and exported helper surface truthfulness.
- It does not claim tty registration parity, notifier execution, khvcd worker execution, live sysrq dispatch, or watchdog core integration.
- Any new driver-local handoff belongs in the dedicated `hvc_console` or watchdog lanes instead of widening this shared packet.
