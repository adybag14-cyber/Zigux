# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current
`master`.
It stays inside the simple-driver lane and records the smaller authenticated
current-head companion packet that remains directly reviewable after older
public-readback wording drifted ahead of current contents reads.
The original archival landing happened on `P11-L13`, while the currently
coupled continuity remains parked under `P11-L16`.

## Status

- `PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`
- archival landing lane: `P11-L13`
- current coupled packet continuity: `P11-L16`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- the Phase 11 roadmap still keeps `drivers/tty/hvc/*.zig` inside bounded
  simple-production-driver work where teardown parity and failure-mode
  reviewability should deepen before any live execution claims
- current authenticated contents readback keeps the bounded HVC current-head
  packet reviewable through:
  - `drivers/tty/hvc/hvc_console.zig`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  - `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- current authenticated contents readback still does not rematerialize
  `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`,
  `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `Documentation/zigux/phase11-hvc-console-slice.md`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`, or
  `scripts/zigux/check-phase11-hvc-survey-packet.py`, so keep that older
  starter-depth packet framed as archival or repo-reality-gap vocabulary until
  a future reread proves those deeper anchors returned
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`
  route
- remaining unported work is still tty-driver registration, khvcd worker
  execution, live sysrq execution, notifier callback execution, and host-backed
  transport or teardown validation

## Current-Head Packet

Treat the current bounded HVC packet on `master` as the smaller authenticated
current-head packet below:

- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

The shared build inventory still records three proof-backed build tests and no
dedicated survey replay entries, which matches that narrower current-head
packet rather than the older starter-depth packet.

## Still-Bounded Gaps

Keep the deeper verify helper, sysrq helper, focused survey replay, manifest,
teardown note, slice, and dedicated survey checker framed as archival or
repo-reality-gap vocabulary until a future reread proves they returned beside
the smaller companion packet.

Keep `zigux/Makefile` explicit only as the returned file; it still does not
prove a dedicated `make -C zigux phase11-hvc-survey` route.

Keep the lane below live tty registration, notifier callback execution, khvcd
execution, live sysrq dispatch, and host-backed teardown parity.

## What Landed

The archival lane recorded a broader HVC starter-depth packet.
Current authenticated contents reads now keep only the direct starter plus the
smaller companion, boundary-note, matrix, checker, inventory, and proof-backed
adjunct stack directly reviewable on `master`.

This survey therefore keeps the current-head packet honest without reviving the
older manifest, teardown-note, survey-checker, helper, or replay anchors as if
they had all returned.

## Bounded Meaning

This note records that the HVC simple-driver lane still has reviewable
current-head continuity through the direct starter, the companion reminder
stack, and the proof-backed adjunct replays listed above.

It does not claim live tty-driver registration, notifier callback execution,
khvcd polling execution, live sysrq dispatch, host-backed cleanup, or
hardware-validated teardown parity.

If a future reread rematerializes the deeper HVC helper, replay, manifest, or
checker anchors, refresh this survey, the validation matrix, and the coupled
current-head checker together in one bounded pass.
