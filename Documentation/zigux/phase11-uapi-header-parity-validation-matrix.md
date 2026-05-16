# Phase 11 UAPI Header Parity Validation Matrix

This document records the bounded shared validation matrix for the Phase 11 UAPI header-parity packet.

## Status

- `PHASE11_UAPI_HEADER_MATRIX_STATUS=shared_header_matrix_landed`
- lane: `P11-L02`
- reviewed against live `master`
- surveyed packet checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the shared header-boundary packet honest about the public `watchdog_info` and `winsize` layouts, the exported `hvc_console.h` constants and helper declarations, and the shared replay route without widening into tty-core or watchdog-core ownership
- current repo reality:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `drivers/tty/hvc/hvc_console.h`
  - `make -C zigux phase11`

## Why This Exists

The shared Phase 11 packet already carries a survey note, a manifest, a deterministic checker, and a shared replay hook for the public header boundary. What it did not have was one bounded matrix note spelling out which proofs are already machine-checked today and which ones are still only note-level follow-through.

Current `master` materially proves the `watchdog_info` and `winsize` layouts, the `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` constants, and the exported `hvc_instantiate`, `hvc_alloc`, `hvc_remove`, `hvc_poll`, `hvc_kick`, `__hvc_resize`, `notifier_add_irq`, `notifier_del_irq`, and `notifier_hangup_irq` declarations through the shared survey gate. The shared note also names a bounded `hv_ops` callback-table layout proof, but that callback-table layout is not yet spelled out as a direct machine-checked assertion in the live survey source. This matrix keeps that difference explicit so the packet stays truthful.

## Kernel-Integration Matrix

lane surface: shared replay route
current evidence: `zigux/tests/phase11_build.zig` still wires `phase11-uapi-header-parity-survey-tests` into the shared `test` step, and `zigux/tests/fixtures/phase11_build_inventory.json` keeps that same survey test in the shared Phase 11 inventory.
replay or checker today: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`, `make -C zigux phase11`, and `scripts/zigux/check-phase11-header-boundary-packet.py`
next bounded follow-up: keep the shared route markers and the shared inventory packet aligned when the header-boundary survey changes again.
out of scope for now: dedicated driver-local teardown, notifier execution, or tty-registration routes.

lane surface: watchdog public header layout
current evidence: `zigux/tests/phase11_uapi_header_parity_survey.zig` keeps `struct watchdog_info` machine-checked at size `40`, alignment `4`, and field offsets `0`, `4`, and `8`.
replay or checker today: shared survey replay through `phase11-uapi-header-parity-survey-tests` and the fail-closed header-boundary checker.
next bounded follow-up: keep the watchdog header checkpoint aligned with the shared note and manifest if the public struct changes.
out of scope for now: `watchdog_device` ownership, registration, and hardware-backed watchdog behavior.

lane surface: tty public winsize layout
current evidence: `zigux/tests/phase11_uapi_header_parity_survey.zig` keeps `struct winsize` machine-checked at size `8`, alignment `2`, and field offsets `0`, `2`, `4`, and `6`.
replay or checker today: shared survey replay through `phase11-uapi-header-parity-survey-tests` and the fail-closed header-boundary checker.
next bounded follow-up: keep the winsize proof aligned with the shared survey note and the shared packet inventory.
out of scope for now: tty-core resize execution and runtime console state changes.

lane surface: exported HVC header constants and declarations
current evidence: `zigux/tests/phase11_uapi_header_parity_survey.zig` checks `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, and the exported `hvc_console.h` declarations for `hvc_instantiate`, `hvc_alloc`, `hvc_remove`, `hvc_poll`, `hvc_kick`, `__hvc_resize`, `notifier_add_irq`, `notifier_del_irq`, and `notifier_hangup_irq`.
replay or checker today: shared survey replay, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, and `scripts/zigux/check-phase11-header-boundary-packet.py`.
next bounded follow-up: keep the note, manifest, and survey source equally explicit if the exported helper surface grows.
out of scope for now: live notifier callback execution, khvcd execution, and host-backed HVC I/O.

lane surface: `hv_ops` callback-table layout proof
current evidence: `Documentation/zigux/phase11-uapi-header-parity-survey.md` names a bounded `hv_ops` layout checkpoint, but the live survey source still focuses on direct header-string and public-struct assertions rather than a dedicated callback-table layout assertion block.
replay or checker today: note-level visibility only; no dedicated `hv_ops` layout assertion is called out as landed machine-checked evidence in the current shared survey source.
next bounded follow-up: add one direct shared-survey proof for `struct hv_ops` size, alignment, and callback offsets so the note-level reminder becomes landed evidence.
out of scope for now: notifier callback semantics, host-backed hypervisor transport, and tty-core registration ownership.

## Why This Stays Bounded

- This matrix is a shared header-boundary truthfulness aid, not a new driver-local lane.
- It does not claim runtime notifier behavior, khvcd worker execution, tty registration, sysrq execution, or watchdog-core integration.
- Any future `hv_ops` layout proof should stay inside the same shared survey packet instead of widening into broader HVC teardown or transport claims.
