# Phase 11 HVC Console Validation Matrix

This document records the bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`
- lane: `P11-L16`
- reviewed against live `master`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the current archived HVC packet honest about what is already reviewable, keep the direct companions explicit, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `drivers/tty/hvc/hvc_console_verify.zig`
  - `drivers/tty/hvc/hvc_console_sysrq.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_cleanup.zig`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_modem_control_split.zig`
  - `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-console-slice.md`
  - `Documentation/zigux/phase11-hvc-console-teardown-note.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `scripts/zigux/check-phase11-hvc-survey-packet.py`
  - `make -C zigux phase11-hvc-survey`
  - `.github/workflows/zigux-bootstrap.yml`

Current `master` also materializes direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions.
The archived HVC packet keeps those direct replay and cleanup surfaces explicit without widening into live notifier, khvcd, or host-backed execution claims.

## Why This Exists

The bounded archival packet now keeps the direct `drivers/tty/hvc/hvc_console.zig` starter, the direct verify and cleanup companions, the final-close teardown summary, explicit close-wait ownership, the `hvc_cleanup()` tty-port release handoff, cleanup-time tty-port ownership, the notifier-add open handoff, the khvcd polling-contract summary, the khvcd worker-entry summary, the `hvc_hangup()` disconnect summary, the `hvc_remove()` handoff summary, the `hvc_kick()` wakeup cue, the targetless notifier no-unregister edge, and the sysrq handoff-versus-literal fallback split reviewable through the survey gate, manifest-backed survey note, slice note, teardown note, validation matrix, shared build inventory, and `drivers/tty/hvc/hvc_console_sysrq.zig`.

This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the archival survey packet
- which teardown-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which direct companions are already landed bounded evidence and how they stay below broader closure claims
- which areas must remain out of scope until a later kernel-facing handoff lands

## Kernel-Integration Matrix

| lane surface | current evidence | archival gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| archival survey gate | `zigux/tests/phase11_hvc_console_survey.zig` plus `zigux/tests/phase11_hvc_console_manifest.json` keep the archived packet, the exported-helper signature proof, the reviewable teardown handoff wording, the `hvc_kick()` wakeup cue, the poll-retry sysrq handoff-versus-literal split, and the direct verify, replay, and cleanup companions explicit beside the survey note | `make -C zigux phase11-hvc-survey` archival route fail-closed through `scripts/zigux/check-phase11-hvc-survey-packet.py` and `.github/workflows/zigux-bootstrap.yml` | keep the same archival packet stable while the next same-lane repair stays inside a host-free notifier, remove, cleanup, or sysrq handoff | live tty registration, notifier callback execution, khvcd worker execution, and host-backed transport |
| teardown summary boundary | `Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps final-close teardown boundaries, close-wait ownership, cleanup tty-port release handoff, cleanup-time tty-port ownership, `hvc_remove()` handoff ordering, and `summarizeNotifierAddOutcome()` readable beside the archived packet without claiming runtime callback execution or host-backed cleanup | the archival survey gate, teardown note, validation matrix, and shared build inventory stay coupled by the HVC packet checker so teardown wording drifts fail closed | keep the same teardown wording aligned while broader teardown ownership remains deferred | live tty core teardown, backend drain timing, and host-backed cleanup |
| sysrq helper boundary | `drivers/tty/hvc/hvc_console_sysrq.zig` plus the survey gate and survey note keep sysrq toggle handoff, pending-dispatch separation, literal-byte fallback on non-kernel `^O`, and post-teardown unavailability explicit without claiming live sysrq dispatch | the archival survey gate and packet checker keep the helper-facing sysrq wording coupled to the bounded HVC packet | keep the helper packet aligned while the lane stays below live console dispatch and transport work | live sysrq dispatch, host-backed console delivery, and runtime keyboard-path integration |
| direct companion surfaces | `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` are now called out through the survey note, slice note, teardown note, validation matrix, shared replay contract, shared build inventory, and tests-root guidance as landed bounded evidence instead of a missing companion gap | the dedicated survey route, packet checker, and shared build inventory keep those direct companions explicit and fail closed if wording drifts back into treating them as absent or into broader closure claims | if one of those direct companions broadens later, update only the same-packet HVC governance surfaces and checker to match the newly landed scope | broader runtime-parity closure, shared Phase 11 closure claims, and non-HVC driver work |

## Failure-Mode Evidence

- final-close teardown wording, explicit close-wait ownership, and cleanup-time tty-port ownership stay explicit through the driver starter, the survey gate, the survey note, the teardown note, and this matrix without claiming runtime callback delivery or host-backed cleanup.
- the direct verify, replay, and cleanup companions stay explicit as landed bounded evidence beside the survey gate, the shared build inventory, and the current review packet so the archived HVC packet no longer drifts back into a stale missing-companion story.
- notifier-add success and the targetless notifier no-unregister edge remain visible through the archived survey surfaces without widening into notifier callback execution.
- the `hvc_kick()` wakeup cue plus the poll-retry sysrq handoff-versus-literal split stay explicit through the survey gate, the poll-retry split, and the survey note so wakeup and pending-dispatch failure-mode boundaries remain reviewable without claiming live poll execution.
- sysrq toggle handoff, pending-dispatch separation, literal-byte fallback, and post-teardown unavailability stay explicit beside `drivers/tty/hvc/hvc_console_sysrq.zig` so the packet keeps bounded sysrq edges visible without claiming live dispatch.
- `summarizeNotifierAddOutcome()` keeps the notifier-facing teardown and failed-open cleanup boundary readable without claiming live callback execution.

## Replay Posture

- the dedicated archival replay remains separate through `make -C zigux phase11-hvc-survey`
- the HVC packet checker continues to keep the survey gate, survey note, slice note, teardown note, validation matrix, modem-control split, poll-retry split, sysrq helper, and shared build inventory aligned with current repo reality
- the shared Phase 11 reminder packet should name the direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions as landed bounded evidence instead of repo-reality gaps
- the shared Phase 11 packet still references this lane through `Documentation/zigux/phase11-shared-replay-contract.md`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `.github/workflows/zigux-bootstrap.yml` without absorbing the driver-local archival wording into a broader closure claim

## Review Rules

- treat this lane as an archival survey, teardown, helper-boundary, and governance packet while live notifier registration, callback execution, tty-driver registration, and host-backed I/O stay out of scope
- treat `zigux/tests/phase11_hvc_console_manifest.json` and `Documentation/zigux/phase11-hvc-console-survey.md` as the landing checkpoint for the archived packet at `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`, not as a rolling promise about runtime parity
- keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned whenever the close, remove, notifier-add, khvcd polling-contract, hangup-disconnect, or direct-companion wording changes
- keep `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `make -C zigux phase11-hvc-survey`, and the survey-backed packet aligned whenever the archival HVC split changes so the lane stays reviewable and the dedicated route keeps failing closed
- do not claim notifier callbacks, khvcd execution, live sysrq dispatch, host-backed I/O coverage, or overall Phase 11 closure from the shipped dedicated `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions alone
- keep the next same-lane repair inside a host-free khvcd, notifier, remove, or cleanup handoff before widening any execution-facing behavior
