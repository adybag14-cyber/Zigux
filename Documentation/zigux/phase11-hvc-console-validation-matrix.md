# Phase 11 HVC Console Validation Matrix

This document records the first bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`
- scope: keep the current `hvc_console` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_cleanup.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `scripts/zigux/check-phase11-shared-replay-contract.py`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers slot validation, CRLF framing, flush-progress intent, the oversized-write failure guard, teardown, the final-close wait boundary, the `hvc_cleanup()` tty-port release handoff, the remove-path handoff, the tty-registration handoff summary, the sysrq handoff summary, and the notifier-facing handoff summary, including the targetless notifier no-unregister edge. The live shared Phase 11 packet already couples those HVC-specific replays to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, which keep the dedicated `zigux/tests/phase11_hvc_cleanup.zig` teardown replay explicit inside the wider `make -C zigux phase11` route while preserving the focused shared header-boundary packet beside the broader driver-local HVC note and survey. This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which teardown-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which areas must remain out of scope until a later kernel-facing handoff lands

Without this matrix, the slice named the right next step but did not yet preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| early-console slot validation | `drivers/tty/hvc/hvc_console.zig` validates slot range, adapter presence, and `removed_vtermno` handling through `HvcConsoleLab.init()`, `instantiate()`, and `teardown()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet recorded by `Documentation/zigux/phase11-shared-replay-contract.md` and replayed in `.github/workflows/zigux-bootstrap.yml` | keep the same slot and teardown evidence aligned with the landed notifier-facing handoff summary | live early-console registration, notifier callbacks, and host-backed reads or writes |
| close-wait teardown boundary | `summarizeCloseBoundary()` records final-close, hung-up close, `HVC_CLOSE_WAIT`-shaped wait intent, and `port_initialized` clearing without claiming live tty teardown | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the final-close and hung-up-close checks in `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet | keep the same final-close evidence stable while the lane stays parked for another comparably small host-free follow-up | real tty core teardown, khvcd worker wakeups, and backend drain timing |
| cleanup tty-port release handoff | `summarizeCleanupHandoff()` keeps final-close and hangup-driven `tty_port_put()` release reviewable, now fails closed if the tty-port reference is already gone, and still leaves final destruction deferred to the tty-port lifecycle | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the dedicated final-close, hangup, and missing-reference cleanup checks in `zigux/tests/phase11_hvc_cleanup.zig`, kept explicit by `Documentation/zigux/phase11-shared-replay-contract.md` inside the shared Phase 11 packet | leave this helper parked unless another comparably small host-free notifier split is clearer than widening further into teardown ownership | real tty-port destructor timing, notifier callback execution, and host-backed teardown drains |
| remove-path teardown handoff | `summarizeRemoveHandoff()` keeps console-slot clearing, preserved IRQ ownership for the later hangup, `tty_port_put()` release, and conditional `tty_vhangup()` then `tty_kref_put()` ordering reviewable without claiming live tty removal | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-path teardown assertions in `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet | leave this handoff parked unless another comparably small host-free notifier split is obvious | live tty removal, notifier callback execution, and host-backed teardown timing |
| console write-path framing | `stageWrite()` covers CRLF framing, retry-after-`-EAGAIN`, partial-write, full-write, fatal-drop bookkeeping, and the `error.InputTooLarge` oversized-write guard without claiming hypervisor I/O | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the framing, flush-progress, and oversized-write checks in `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet | keep the flush-progress and oversized-write guard surface stable while notifier and sysrq boundaries stay reviewable without widening into backend transport code | host-backed putchars calls, sysrq dispatch, and khvcd polling loops |
| tty registration and khvcd behavior | `summarizeTtyRegistrationHandoff()` now records `setup_hvc_console()` registration intent, close-wait ownership, console-binding retention, khvcd wakeup visibility, and the still-deferred worker-execution boundary without claiming live tty registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the tty-registration handoff assertions in `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet | keep this handoff aligned with the landed notifier-facing summary instead of widening into worker execution | full tty-driver registration, notifier callback execution, khvcd thread lifecycle, hotplug discovery, and live hypervisor transport |
| sysrq dispatch boundary | `summarizeSysrqHandoff()` now records boot-console-only sysrq dispatch intent, break detection, deferred notifier callbacks, and the still-deferred worker-execution boundary without claiming live sysrq handling | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the sysrq handoff assertions in `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet | keep this handoff aligned with the landed notifier-facing callback-ownership summary instead of widening into live dispatch or host-backed console reads | real sysrq dispatch, notifier callback execution, khvcd worker execution, and live hypervisor transport |
| notifier callback boundary | `summarizeNotifierHandoff()` now records tty-registration readiness, notifier target presence, deferred callback ownership, deferred unregister timing, the never-registered path where unregister timing stays false because tty registration never became ready, and the targetless path where unregister timing also stays false because no notifier target was wired, without claiming live notifier registration or callback execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the notifier handoff assertions, including the dedicated targetless no-unregister replay, in `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet recorded by `Documentation/zigux/phase11-shared-replay-contract.md` | keep this handoff stable while the next follow-through stays inside shared review truthfulness instead of widening into live callback execution | live notifier registration, callback execution, khvcd worker execution, and host-backed hypervisor transport |

## Review Rules

- treat this lane as a bounded driver-starter plus handoff-note lane while live notifier registration, callback execution, and host-backed I/O stay out of scope
- treat `zigux/tests/phase11_hvc_console_manifest.json` and `Documentation/zigux/phase11-hvc-console-survey.md` as the archival landing checkpoint for the bounded starter, not as a rolling promise about the current `master` head
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with this matrix whenever the shared-versus-dedicated HVC replay split changes so the dedicated `hvc_cleanup()` teardown replay stays explicit inside the wider Phase 11 packet and the focused shared header-boundary packet stays visible beside it
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter while the dedicated archival `make -C zigux phase11-hvc-survey` bootstrap replay remains the only extra CI step for the separate survey route
- do not claim notifier callbacks, khvcd execution, live sysrq dispatch, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist
- when a later callback-execution slice lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
