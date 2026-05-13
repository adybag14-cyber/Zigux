# Phase 11 HVC Console Validation Matrix

This document records the bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`
- lane: `P11-L16`
- reviewed against live `master`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the current archived HVC packet honest about what is already reviewable, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_modem_control_split.zig`
  - `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
  - `drivers/tty/hvc/hvc_console_sysrq.zig`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-console-slice.md`
  - `Documentation/zigux/phase11-hvc-console-teardown-note.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `scripts/zigux/check-phase11-hvc-survey-packet.py`
  - `make -C zigux phase11-hvc-survey`
  - `.github/workflows/zigux-bootstrap.yml`

The still-absent direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions remain repo-reality gaps. Keep those gaps explicit beside the archived HVC packet without widening the lane into live notifier, khvcd, or host-backed execution claims.

## Why This Exists

The bounded archival packet now keeps the direct `drivers/tty/hvc/hvc_console.zig` starter, the still-absent direct companion trio, the final-close teardown summary, the `hvc_cleanup()` tty-port release handoff, the notifier-add open handoff, the `hvc_remove()` handoff summary, the `hvc_kick()` wakeup cue, the targetless notifier no-unregister edge, and the sysrq handoff-versus-literal fallback split reviewable through the survey gate, manifest-backed survey note, slice note, teardown note, validation matrix, and `drivers/tty/hvc/hvc_console_sysrq.zig`.

This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the archival survey packet
- which teardown-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which repo-reality gaps still need to remain explicit until a later same-lane follow-through lands
- which areas must remain out of scope until a later kernel-facing handoff lands

Without this matrix, the archival packet names the right follow-through but does not preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | archival gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| archival survey gate | `zigux/tests/phase11_hvc_console_survey.zig` plus `zigux/tests/phase11_hvc_console_manifest.json` keep the archived packet, the explicit repo-reality gap where no separate direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, or `zigux/tests/phase11_hvc_cleanup.zig` companions ship on current `master`, the exported-helper signature proof, the reviewable teardown handoff wording, the `hvc_kick()` wakeup cue, and the poll-retry sysrq handoff-versus-literal split visible beside the survey note | `make -C zigux phase11-hvc-survey` archival route fail-closed through `scripts/zigux/check-phase11-hvc-survey-packet.py` and `.github/workflows/zigux-bootstrap.yml` | keep the same archival packet stable while the next same-lane repair stays inside a host-free notifier, remove, cleanup, or sysrq handoff | live tty registration, notifier callback execution, khvcd worker execution, and host-backed transport |
| teardown summary boundary | `Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps final-close teardown boundaries, cleanup tty-port release handoff, and `hvc_remove()` slot-release ordering readable beside the archived packet without claiming direct replay or cleanup companion files that current `master` does not ship | the archival survey gate, teardown note, and survey note stay coupled by the HVC packet checker so teardown wording drifts fail closed | keep the same teardown wording aligned while broader teardown ownership remains deferred | live tty core teardown, backend drain timing, and host-backed cleanup |
| sysrq helper boundary | `drivers/tty/hvc/hvc_console_sysrq.zig` plus the survey gate and survey note keep sysrq toggle handoff, pending-dispatch separation, literal-byte fallback on non-kernel `^O`, and post-teardown unavailability explicit without claiming live sysrq dispatch | the archival survey gate and packet checker keep the helper-facing sysrq wording coupled to the bounded HVC packet | keep the helper packet aligned while the lane stays below live console dispatch and transport work | live sysrq dispatch, host-backed console delivery, and runtime keyboard-path integration |
| direct companion gap | the survey gate, survey note, slice note, teardown note, validation matrix, and checker all now make the missing direct companion trio explicit instead of presenting them as landed replay evidence | the dedicated survey route and packet checker keep those repo-reality gaps visible and fail closed if the wording drifts back into overclaiming | if one of those direct companions lands later, update only the same-packet HVC governance surfaces and checker to match the newly landed scope | broader runtime-parity closure, shared Phase 11 closure claims, and non-HVC driver work |

## Failure-Mode Evidence

- final-close teardown wording stays explicit through the driver starter, the survey gate, the survey note, the teardown note, and this matrix without claiming direct replay or cleanup companions that current `master` does not ship.
- the direct companion trio remains explicitly absent through the survey gate, survey note, slice note, teardown note, checker, and this matrix so the archived packet does not quietly grow replay or cleanup claims that current `master` cannot support.
- notifier-add success and the targetless notifier no-unregister edge remain visible through the archived survey surfaces without widening into notifier callback execution.
- the `hvc_kick()` wakeup cue plus the poll-retry sysrq handoff-versus-literal split stay explicit through the survey gate, the poll-retry split, and the survey note so wakeup and pending-dispatch failure-mode boundaries remain reviewable without claiming live poll execution.
- sysrq toggle handoff, pending-dispatch separation, literal-byte fallback, and post-teardown unavailability stay explicit beside `drivers/tty/hvc/hvc_console_sysrq.zig` so the packet keeps bounded sysrq edges visible without claiming live dispatch.

## Replay Posture

- the dedicated archival replay remains separate through `make -C zigux phase11-hvc-survey`
- the HVC packet checker continues to keep the survey gate, survey note, slice note, teardown note, validation matrix, modem-control split, poll-retry split, and sysrq helper aligned with current repo reality
- the shared Phase 11 reminder packet should name the still-absent direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions as repo-reality gaps instead of shipped evidence
- the shared Phase 11 packet still references this lane through `Documentation/zigux/phase11-shared-replay-contract.md` and `.github/workflows/zigux-bootstrap.yml` without absorbing the driver-local archival wording into a broader closure claim

## Review Rules

- treat this lane as an archival survey, teardown, helper-boundary, and governance packet while live notifier registration, callback execution, tty-driver registration, and host-backed I/O stay out of scope
- treat `zigux/tests/phase11_hvc_console_manifest.json` and `Documentation/zigux/phase11-hvc-console-survey.md` as the landing checkpoint for the archived packet at `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`, not as a rolling promise about runtime parity
- keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned whenever the close, remove, notifier-add, khvcd polling-contract, hangup-disconnect, or direct-companion gap wording changes
- keep `scripts/zigux/check-phase11-hvc-survey-packet.py`, `make -C zigux phase11-hvc-survey`, and the survey-backed packet aligned whenever the archival HVC split changes so the lane stays reviewable and the dedicated route keeps failing closed
- do not claim notifier callbacks, khvcd execution, live sysrq dispatch, host-backed I/O coverage, or shipped dedicated `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, or `zigux/tests/phase11_hvc_cleanup.zig` companions as landed
- keep the next same-lane repair inside a host-free khvcd, notifier, remove, cleanup, or direct-companion-gap truthfulness handoff before widening any execution-facing behavior
