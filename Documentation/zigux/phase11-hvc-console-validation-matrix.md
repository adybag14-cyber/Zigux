# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=driver_anchor_returned_current_head_compile_verified`
- lane: `P11-L15`
- reviewed against live `master`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the returned `hvc_console` driver anchor and the surviving HVC
  packet truthful without widening into live tty registration, notifier callback
  execution, khvcd worker execution, live sysrq dispatch, or host-backed
  teardown
- current direct-readback packet in this lane:
  - `drivers/tty/hvc/hvc_console.zig`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
- attached-toolchain replay for this lane now succeeds on the returned direct
  driver anchor through `zig test drivers/tty/hvc/hvc_console.zig` replayed from
  current-head readback, with all 23 bundled driver tests passing in scratch
- current direct contents reads in this lane still do not rematerialize
  `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`,
  `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `zigux/tests/phase11_hvc_console_modem_control_split.zig`,
  `zigux/tests/phase11_hvc_console_poll_retry_split.zig`,
  `Documentation/zigux/phase11-hvc-console-slice.md`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`,
  `Documentation/zigux/phase11-shared-replay-contract.md`,
  `scripts/zigux/check-phase11-hvc-survey-packet.py`, and
  `make -C zigux phase11-hvc-survey`, so keep those paths framed as same-lane
  archival vocabulary or repo-reality gaps until a future reread proves they
  returned
- current `master` still does materialize `zigux/Makefile`, but its live body
  does not expose a dedicated Phase 11 build or survey route, so keep the
  returned file distinct from the still-missing Phase 11 route names

## Why This Exists

The bounded Phase 11 HVC lane still needs one reviewable matrix note, but that
note now has to match a split current-head reality: the direct `hvc_console`
driver anchor has returned and compiles cleanly in a narrowed attached-toolchain
replay, while the broader starter-depth companion packet and dedicated survey
route still do not rematerialize through this lane's current contents reads.

This matrix therefore records current-head truthfulness for the returned driver
anchor plus the surviving HVC reminder surfaces, instead of collapsing back to
either the older fully returned starter-depth packet or the later proof-only
packet that treated the direct driver itself as missing.

## Current-Head Matrix

| lane surface | current evidence | bounded gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| direct driver compile replay | `drivers/tty/hvc/hvc_console.zig` now rematerializes on current `master`, and the returned driver still carries reviewable summaries for final-close teardown ownership, cleanup-time tty-port ownership, wakeup cues, targetless notifier edges, notifier IRQ helper behavior, modem-control helper behavior, and the broader bounded HVC handoff surface | attached Zig replay of the returned driver anchor keeps the same bounded direct-driver packet compile-valid with all 23 bundled tests passing in scratch | if another same-lane drift appears, start from the returned driver anchor and keep the follow-through to one driver-local compile or truthfulness repair only | live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, host-backed cleanup, and hardware-backed teardown |
| shared survey and matrix posture | `Documentation/zigux/phase11-hvc-console-survey.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md` still rematerialize on current `master`, so the HVC lane keeps one direct survey surface and one direct matrix surface beside the returned driver anchor | this matrix and the surviving survey note keep the returned direct driver anchor separate from the still-missing companion replay packet and route names | refresh the survey and matrix together if a future reread changes which same-lane anchors rematerialize | using the returned survey and matrix to overclaim broader replay or execution parity |
| starter-depth companion packet | the broader same-lane companion family still does not rematerialize in this lane through current contents reads: verify helper, sysrq helper, focused replay files, survey gate, manifest, split replays, teardown note, shared replay contract, dedicated checker, and dedicated survey route remain archival vocabulary or repo-reality gaps | keep the returned driver anchor explicit without treating the missing companion packet as back on current head | if direct rereads rematerialize one or more missing companion anchors, refresh this matrix and the coupled survey note in one bounded pass | turning historical packet membership into current-head proof without fresh readback |
| shared route boundary | `zigux/Makefile` is readable again on current `master`, but its body still exposes no dedicated Phase 11 route, so the returned file must stay distinct from missing names such as `make -C zigux phase11-hvc-survey` or any broader Phase 11 build handle | the survey note and contributor-facing reminders keep returned files distinct from still-missing Phase 11 route names | keep broad reminders aligned with the returned Makefile posture until a future reread proves a dedicated Phase 11 route returned | reviving missing Phase 11 routes from historical wording alone |

## Failure-Mode Evidence

- The returned direct driver anchor still keeps close-path ownership explicit
  through `summarizeCloseTeardown()` with `close_wait_ownership` and keeps
  cleanup-time tty-port ownership explicit through `summarizeCleanupHandoff()`.
- The same returned driver anchor still keeps targetless notifier no-unregister
  behavior, notifier IRQ helper boundaries, wakeup-cue visibility, and
  modem-control helper boundaries reviewable without claiming live notifier or
  host-backed execution.
- The attached-toolchain scratch replay for the returned
  `drivers/tty/hvc/hvc_console.zig` anchor now passes all 23 bundled driver
  tests, so the direct driver anchor is current-head compile-verified even while
  the broader companion packet remains missing in this lane.
- The companion verify helper, sysrq helper, focused replay files, teardown
  note, survey checker, and dedicated survey route remain same-lane archival
  vocabulary or repo-reality gaps until direct rereads rematerialize them again.

## Replay Posture

- Treat `drivers/tty/hvc/hvc_console.zig`,
  `Documentation/zigux/phase11-hvc-console-survey.md`, and
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md` as the truthful
  current-head HVC packet that this lane can directly read today.
- Treat the returned `hvc_console` driver anchor as compile-verified at bounded
  starter depth through the attached Zig replay, not as proof that the broader
  helper, replay, survey-gate, teardown-note, or route packet has returned.
- Keep the companion verify, sysrq, replay, split, teardown-note, checker, and
  dedicated route family framed as archival vocabulary or repo-reality gaps
  until current direct reads recover them.
- Keep `zigux/Makefile` explicit only as the returned file; do not treat it as
  proof that a dedicated Phase 11 HVC route has come back.

## Review Rules

- Do not claim `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`,
  `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `zigux/tests/phase11_hvc_console_modem_control_split.zig`,
  `zigux/tests/phase11_hvc_console_poll_retry_split.zig`,
  `Documentation/zigux/phase11-hvc-console-slice.md`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`,
  `Documentation/zigux/phase11-shared-replay-contract.md`,
  `scripts/zigux/check-phase11-hvc-survey-packet.py`, or
  `make -C zigux phase11-hvc-survey` as direct current-head evidence unless a
  future reread proves they rematerialized.
- If the returned direct driver anchor or the surviving survey-plus-matrix pair
  changes, update those same-lane surfaces together in one bounded pass.
- Do not widen this matrix into notifier callback execution, tty registration,
  khvcd worker execution, live sysrq dispatch, host-backed teardown, or overall
  Phase 11 closure claims.
