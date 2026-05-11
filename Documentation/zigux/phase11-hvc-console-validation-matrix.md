# Phase 11 HVC Console Validation Matrix

This document records the bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`
- lane: `P11-L16`
- reviewed against live `master` `16c6f699e6d4e6a0466d4e6a0466d4e6a0466d4e`
- scope: keep the current `hvc_console` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `drivers/tty/hvc/hvc_console_verify.zig`
  - `drivers/tty/hvc/hvc_console_sysrq.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_cleanup.zig`
  - `zigux/tests/phase11_hvc_console_modem_control_split.zig`
  - `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-console-slice.md`
  - `Documentation/zigux/phase11-hvc-console-teardown-note.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `scripts/zigux/check-phase11-hvc-survey-packet.py`
  - `make -C zigux phase11-hvc-survey`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers slot validation, CRLF framing, flush-progress intent, the oversized-write failure guard, teardown, the final-close wait boundary, the `hvc_cleanup()` tty-port release handoff, the remove-path handoff, the tty-registration handoff summary, the sysrq handoff summary, and the notifier-facing handoff summary, including the targetless notifier no-unregister edge. The live shared Phase 11 packet already couples those HVC-specific replays to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, which keep the dedicated `zigux/tests/phase11_hvc_cleanup.zig` teardown replay and the compile-local `drivers/tty/hvc/hvc_console_verify.zig` teardown, cleanup-prerequisite, sysrq, and notifier-failure replays explicit inside the wider `make -C zigux phase11` route while preserving the focused shared header-boundary packet beside the broader driver-local HVC note and survey and keeping the dedicated `make -C zigux phase11-hvc-survey` archival route fail-closed.

This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which teardown-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which areas must remain out of scope until a later kernel-facing handoff lands

Without this matrix, the slice named the right next step but did not yet preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| early-console slot validation | `drivers/tty/hvc/hvc_console.zig` validates slot range, adapter presence, and `removed_vtermno` handling through `HvcConsoleLab.init()`, `instantiate()`, and `teardown()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 replay packet recorded by `Documentation/zigux/phase11-shared-replay-contract.md` and replayed in `.github/workflows/zigux-bootstrap.yml` | keep the same slot and teardown evidence aligned with the landed notifier-facing handoff summary | live early-console registration, notifier callbacks, and host-backed reads or writes |
| close-wait teardown boundary | `summarizeCloseBoundary()` records final-close, hung-up close, `HVC_CLOSE_WAIT`-shaped wait intent, and `port_initialized` clearing without claiming live tty teardown, while `drivers/tty/hvc/hvc_console_verify.zig` keeps the final-close handoff chain compile-local | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the final-close and hung-up-close checks in `zigux/tests/phase11_hvc_console.zig` plus the compile-local final-close replay in `drivers/tty/hvc/hvc_console_verify.zig` | keep the same final-close evidence stable while the lane stays parked for another comparably small host-free follow-up | real tty core teardown, khvcd worker wakeups, and backend drain timing |
| cleanup tty-port release handoff | `summarizeCleanupHandoff()` keeps final-close and hangup-driven `tty_port_put()` release reviewable, now fails closed if the tty-port reference is already gone, and still leaves final destruction deferred to the tty-port lifecycle | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the dedicated final-close, hangup, and missing-reference cleanup checks in `zigux/tests/phase11_hvc_cleanup.zig`, plus the compile-local final-close, hung-up cleanup, and cleanup-prerequisite failure replays in `drivers/tty/hvc/hvc_console_verify.zig`, kept explicit by `Documentation/zigux/phase11-shared-replay-contract.md` inside the shared Phase 11 packet | leave this helper parked unless another comparably small host-free notifier split is clearer than widening further into teardown ownership | real tty-port destructor timing, notifier callback execution, and host-backed teardown drains |
| `hvc_remove()` handoff | `summarizeRemoveHandoff()` keeps console-slot clearing, preserved IRQ ownership for the later hangup, `tty_port_put()` release, and conditional `tty_vhangup()` then `tty_kref_put()` ordering reviewable without claiming live tty removal, while `drivers/tty/hvc/hvc_console_verify.zig` keeps the detached remove matrix compile-local | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-path teardown assertions in `zigux/tests/phase11_hvc_console.zig` and the hung-up or detached teardown replay in `drivers/tty/hvc/hvc_console_verify.zig` inside the shared Phase 11 replay packet | leave this handoff parked unless another comparably small host-free notifier split is obvious | live tty removal, notifier callback execution, and host-backed teardown timing |
| khvcd polling contract boundary | `summarizeKhvcdPollingContract()` keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, and teardown-facing host-I/O pressure reviewable without claiming khvcd worker execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the khvcd polling-contract assertions in `zigux/tests/phase11_hvc_console.zig` | keep the poll-mask evidence parked unless a later host-free khvcd, notifier, or sysrq split becomes obvious | live khvcd thread scheduling, notifier callbacks, host-backed getchars or putchars execution, and sysrq dispatch |
| notifier callback boundary | `summarizeNotifierHandoff()` now records tty-registration readiness, notifier target presence, deferred callback ownership, deferred unregister timing, the never-registered path where unregister timing stays false because tty registration never became ready, and the targetless path where unregister timing also stays false because no notifier target was wired, without claiming live notifier registration or callback execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the notifier handoff assertions, including the dedicated targetless no-unregister replay, in `zigux/tests/phase11_hvc_console.zig` plus the compile-local notifier prerequisite, never-registered, targetless, and targetless-sysrq failure-mode replays in `drivers/tty/hvc/hvc_console_verify.zig` inside the shared Phase 11 replay packet | keep this handoff stable while the next follow-through stays inside shared review truthfulness instead of widening into live callback execution | live notifier registration, callback execution, khvcd worker execution, and host-backed hypervisor transport |
| notifier-add open handoff | `summarizeNotifierAddOutcome()` keeps notifier-add success, polling fallback, failed-open close cleanup, open-time IRQ request boundaries, and khvcd kick follow-through reviewable without claiming live notifier callback execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the notifier-add success, fallback, and failure cleanup assertions in `zigux/tests/phase11_hvc_console.zig` | leave this handoff parked unless a later host-free notifier callback, sysrq, or khvcd split needs the same open-time evidence | live notifier callback execution, real IRQ enablement, tty-driver registration side effects, and host-backed open recovery |
| `hvc_hangup()` disconnect boundary | `summarizeHangupDisconnect()` keeps resize-work cancellation, the stale-count short-circuit, tty detachment, buffered-write clearing, and `notifier_hangup` ownership reviewable without claiming live callback execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the active-hangup and stale-hangup assertions in `zigux/tests/phase11_hvc_console.zig` | leave this helper parked unless another comparably small host-free notifier callback, sysrq, or khvcd split becomes obvious | live notifier callback execution, remove-time tty ownership races, IRQ teardown, and host-backed disconnect timing |

## Failure-Mode Evidence

- stale hangup short-circuit that preserves buffered-write state when the port count is already zero is pinned separately from the active disconnect path so the bounded helper does not silently borrow remove-time tty ownership or live notifier callbacks.
- cleanup-prerequisite failure replay stays compile-local in `drivers/tty/hvc/hvc_console_verify.zig` so the HVC packet keeps impossible cleanup ownership explicit before any tty-core teardown claim widens.
- notifier-prerequisite and notifierless-open failure replays stay compile-local in `drivers/tty/hvc/hvc_console_verify.zig` so the bounded survey preserves failure-mode parity without claiming live notifier callback execution.
- targetless and no-dispatch sysrq or notifier deferral replays stay explicit beside `drivers/tty/hvc/hvc_console_sysrq.zig` so the packet keeps bounded sysrq handoff visible without claiming live dispatch.

## Replay Posture

- the shared Phase 11 gate for this lane remains `zigux/tests/phase11_build.zig`
- the shared replay continues through `zig build test --build-file zigux/tests/phase11_build.zig --summary all` and the Linux-style wrapper `make -C zigux phase11`
- the dedicated archival survey replay remains separate through `make -C zigux phase11-hvc-survey`
- the dedicated survey gate still runs separately, while the shared starter replay continues to keep teardown, notifier, sysrq, khvcd, and poll-drain surfaces visible together

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane while live notifier registration, callback execution, and host-backed I/O stay out of scope
- treat `zigux/tests/phase11_hvc_console_manifest.json` and `Documentation/zigux/phase11-hvc-console-survey.md` as the archival landing checkpoint for the bounded starter, not as a rolling promise about the current `master` head
- keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned whenever the close, cleanup, remove, khvcd polling-contract, or hangup-disconnect ownership story changes
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with this matrix whenever the shared-versus-dedicated HVC replay split changes so the dedicated `hvc_cleanup()` teardown replay and the compile-local `hvc_console_verify` teardown, cleanup-prerequisite, sysrq, and notifier failure-mode replays stay explicit inside the wider Phase 11 packet, the focused shared header-boundary packet stays visible beside them, and the dedicated archival `phase11-hvc-survey` route keeps failing closed
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter while the dedicated archival `make -C zigux phase11-hvc-survey` bootstrap replay remains the only extra CI step for the separate survey route
- do not claim notifier callbacks, khvcd execution, live sysrq dispatch, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist
- when a later callback-execution slice lands, update this matrix, the slice note, the teardown note, and the survey note together so the lane keeps one truthful next step
- keep the next same-lane repair inside a host-free khvcd, notifier, remove, or cleanup handoff before widening any execution-facing behavior