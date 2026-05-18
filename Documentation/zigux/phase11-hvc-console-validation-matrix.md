# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=proof_backed_current_head_continuity`
- lane: `P11-L16`
- reviewed against live `master`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the current HVC packet truthful without widening into live tty
  registration, notifier callback execution, khvcd worker execution, live sysrq
  dispatch, or host-backed teardown
- current direct-readback packet:
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  - `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- current direct contents reads in this lane still do not rematerialize
  `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`,
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
  `make -C zigux phase11-hvc-survey`, so keep those paths framed as
  survey-recorded archival vocabulary or repo-reality gaps until a future reread
  proves they returned
- current `master` does materialize `zigux/Makefile`, but its live body still
  does not expose a dedicated Phase 11 build or survey route, so keep the
  returned file distinct from the still-missing Phase 11 route names

## Why This Exists

The bounded Phase 11 HVC lane still needs one reviewable matrix note, but that
note has to follow the smaller proof-backed current-head packet now kept honest
by the HVC survey note, the cleanup-alignment companion, the verify-helper
boundary note, the shared build inventory, and the surviving proof shards.

This matrix therefore records current-head truthfulness for the HVC lane rather
than replaying the older starter-depth packet as if its direct anchors and
dedicated survey route were still back on `master`.

## Current-Head Matrix

| lane surface | current evidence | bounded gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| proof-backed continuity packet | `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` keep the current HVC lane reviewable without claiming that the older direct starter or replay anchors have returned | the cleanup-current-head checker plus the narrowed shared build inventory keep the same packet fail-closed | refresh this matrix together with the HVC survey note and the cleanup-alignment companion if that proof-backed packet widens or narrows again | live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, and host-backed teardown |
| shared driver-local matrix posture | `Documentation/zigux/phase11-hvc-console-validation-matrix.md` remains the only directly readable driver-local Phase 11 matrix note on current `master`, while `Documentation/zigux/phase11-validation-matrix-gap-survey.md` and `Documentation/zigux/phase11-driver-lane-sequencing.md` keep that surviving HVC matrix coupled to the smaller current-head shared packet instead of the older replay-contract stack or a no-longer-true four-matrix packet | the matrix-gap survey and shared sequencing note keep this matrix aligned with the surviving HVC-only driver-local readback and the narrowed shared HVC inventory | keep the matrix explicit without using it to overclaim broader replay, route, or execution parity | broader watchdog-core, notifier, sysrq, MMIO, khvcd, or hardware-backed execution claims |
| starter-depth archival packet | `Documentation/zigux/phase11-hvc-console-survey.md` still records the older starter-depth HVC family, but current direct contents reads in this lane do not rematerialize the archived driver, replay, survey-manifest, split, teardown-note, shared-contract, checker, or dedicated survey-route anchors | the survey note now owns that archival vocabulary and keeps it separate from the smaller current-head packet | if direct rereads rematerialize one or more of those missing anchors, refresh this matrix, the HVC survey note, and any coupled checker in one pass | turning archival vocabulary into current-head proof without fresh readback |
| shared route boundary | `zigux/Makefile` is readable again on current `master`, but its body still exposes no dedicated Phase 11 route, so the returned file must stay distinct from missing names such as `make -C zigux phase11-hvc-survey` or any broader Phase 11 build handle | the sequencing note and contributor-facing summaries keep returned files distinct from still-missing Phase 11 route names | keep broad reminders aligned with the returned Makefile posture until a future reread proves a dedicated Phase 11 route returned | reviving missing Phase 11 routes from historical wording alone |

## Failure-Mode Evidence

- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps cleanup
  prerequisite failures, detached-binding remove-handoff boundaries, targetless
  notifier no-unregister behavior, and targetless sysrq separation reviewable as
  direct current-head packet evidence without claiming live callback execution.
- `hvc_cleanup()` tty-port release handoff remains explicit in the current HVC
  packet, but it now stays reviewable through the cleanup-alignment companion,
  the verify-helper boundary note, and the surviving proof-backed cleanup packet
  instead of relying on the older direct replay anchors as current-head
  evidence.
- The final-close and hangup-driven cleanup handoff assertions inside the shared Phase 11 replay remain preserved as bounded HVC cleanup vocabulary, while the current-head packet keeps those boundaries explicit through the surviving proof-backed packet and its coupled reminder notes rather than by treating the older replay family as fully returned direct readback.
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig` keep the surviving
  proof-backed HVC packet explicit on current `master`.
- `zigux/tests/fixtures/phase11_build_inventory.json` now records the narrowed
  current-head HVC continuity packet rather than a whole-Phase-11 replay roster,
  so use it to keep the surviving packet explicit instead of reconstructing the
  missing starter-depth family.
- The archived direct driver, cleanup replay, sysrq helper, modem-control split,
  poll-retry split, dedicated survey replay, shared replay-contract, and
  dedicated survey-route family remain survey-recorded or missing until direct
  rereads rematerialize them again.

## Replay Posture

- Treat `Documentation/zigux/phase11-hvc-console-survey.md`,
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and the surviving
  proof shards as the truthful current-head HVC packet on `master`.
- Keep the direct starter-depth family and the dedicated
  `make -C zigux phase11-hvc-survey` route framed as archival vocabulary or
  repo-reality gaps until current direct reads recover them.
- Keep `zigux/Makefile` explicit only as the returned file; do not treat it as
  proof that a dedicated Phase 11 HVC route has come back.
- Keep this matrix aligned with `Documentation/zigux/phase11-driver-lane-sequencing.md`,
  `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, and the broad
  contributor-facing reminders so the same lane does not split between
  proof-backed current-head wording and replay-contract-era wording.

## Review Rules

- Do not claim `drivers/tty/hvc/hvc_console.zig`,
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
  `scripts/zigux/check-phase11-hvc-survey-packet.py`, or
  `make -C zigux phase11-hvc-survey` as direct current-head evidence unless a
  future reread proves they rematerialized.
- If the proof-backed packet changes, update this matrix together with the HVC
  survey note, the cleanup-alignment companion, and any coupled checker or
  inventory note in the same bounded pass.
- Do not widen this matrix into notifier callback execution, tty registration,
  khvcd worker execution, live sysrq dispatch, host-backed teardown, or overall
  Phase 11 closure claims.
