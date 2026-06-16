# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner
lanes while reflecting only the current-head surfaces that were reread in this
run.

## Scope

Use this note when a Phase 11 change touches the shared reminder packet under
`Documentation/zigux/phase11-*.md`, the coupled
`scripts/zigux/check-phase11-*.py` review surfaces, or the proof-backed or
scaffold-backed Phase 11 files under `zigux/tests/`.

## Lane Split

Keep the current lane split explicit:

- shared sequencing lane `P11-Y06` owns the shared reminder wording in
  `Documentation/zigux/phase11-driver-lane-sequencing.md` and
  `Documentation/zigux/phase11-validation-matrix-gap-survey.md` together with
  the smallest coupled checker updates needed to keep that shared packet honest
- bcm2835 continuity stays separate from the shared sequencing lane, but fresh
  authenticated contents rereads in this run do rematerialize
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so shared-note
  truthfulness work can keep that returned driver-local matrix explicit without
  widening into bcm2835-only reminder wording, replay claims, or platform-backed
  execution
- gpio continuity stays separate from the shared sequencing lane; current
  shared-note work should not reopen gpio reminder wording unless the gpio lane
  itself changes
- DesignWare lane `P11-L10` stays separate from the shared sequencing lane, but
  authenticated contents rereads in this run do rematerialize
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and those same
  current-head rereads also keep the returned DesignWare docs-owner, checker,
  registration-scaffold, the optional APB-clock scaffold outcomes, and adjacent
  PM-helper packet explicit through
  `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
  `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
  `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
  `scripts\zigux/check_phase11_dw_wdt_teardown_packet.zig`,
  `scripts\zigux/check_phase11_dw_wdt_verify_alignment.zig`,
  `zigux/tests/phase11_dw_wdt_manifest.json`,
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
  `drivers/watchdog/dw_wdt_pm.zig`, and
  `drivers/watchdog/dw_wdt_pm_scaffold.zig`, while
  `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and
  `zigux/tests/phase11_dw_wdt.zig` stay framed as repo-reality-gap vocabulary
  until a fresh reread proves they returned, and the older
  `scripts\zigux/check_phase11_dw_wdt_packet.zig` handle stays framed as
  historical vocabulary
- HVC continuity lane `P11-L16` currently keeps the directly readable
  `Documentation/zigux/phase11-hvc-console-survey.md`,
  `drivers/tty/hvc/hvc_console.zig`,
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
  `scripts\zigux/check_phase11_hvc_cleanup_current_head.zig`,
  `scripts\zigux/check_phase11_hvc_targetless_unregister_witness.zig`,
  `zigux/tests/fixtures/phase11_build_inventory.json`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  `zigux/tests/phase11_hvc_modem_control_proof.zig`,
  `zigux/tests/phase11_hvc_modem_control_proof_build.zig`,
  `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, and
  `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` authoritative
  for the current-head continuity packet and helper-local teardown or
  failure-mode evidence while the broader starter-depth archival landing remains
  `P11-L13`; keep the deeper verify helper, sysrq helper, focused survey
  replay, manifest, dedicated survey-checker, and teardown-note anchors framed
  as archival or repo-reality-gap vocabulary until a fresh reread proves they
  returned
- adjacent contributor-note and header-boundary packets stay outside this
  driver-lane split even when this shared note names them as surrounding shared
  evidence; do not treat `P11-L18` or the header-parity packet as driver-lane
  owner surfaces inside `P11-Y06`

## Shared Packet Boundaries

Treat the current shared Phase 11 packet as the reminder and continuity
surfaces that were reread in this run:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `scripts\zigux/check_phase11_matrix_gap_survey.zig`
- `scripts\zigux/check_phase11_validation_matrix_gap_survey.zig`
- `scripts\zigux/check_phase11_build_inventory.zig`
- `scripts\zigux/check_phase11_dw_wdt_teardown_packet.zig`
- `scripts\zigux/check_phase11_dw_wdt_verify_alignment.zig`
- `scripts\zigux/check_phase11_hvc_cleanup_current_head.zig`
- `scripts\zigux/check_phase11_hvc_targetless_unregister_witness.zig`
- `scripts\zigux/validate_phase11.zig`
- `drivers/watchdog/dw_wdt_pm.zig`
- `drivers/watchdog/dw_wdt_pm_scaffold.zig`
- `zigux/Makefile`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

For this driver-lane-only note, the contributor-facing and header-boundary
entries above remain adjacency references rather than `P11-Y06` owner surfaces.
Use them only to keep driver-lane reminders from drifting into non-driver
packets.

Current rereads in this run rematerialized the bcm2835, gpio watchdog, HVC, and
DesignWare driver-local validation matrices named by the roadmap together with the
narrower HVC current-head continuity packet plus its cleanup companion,
current-head checker, dedicated targetless-unregister witness checker, build
inventory, proof-backed adjunct stack, the dedicated modem-control proof pair,
and the standalone targetless-unregister witness pair.
Authenticated contents reads in this run now rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so keep all four
driver-local validation matrices explicit in the shared current-head packet
while leaving bcm2835 and DesignWare reminder follow-through in their own lanes.

Current rereads in this run also keep
`Documentation/zigux/phase11-shared-replay-contract.md` directly readable as an
archival shared reminder surface.
Keep that returned contract explicit in the sequencing packet, but keep its
older paired `scripts\zigux/check_phase11_shared_replay_contract.zig`,
`scripts\zigux/check_phase11_shared_summary_surfaces.zig`, and
`zigux/tests/phase11_build.zig` routes framed as missing current-head
companions rather than live replay evidence.

Current rereads in this run also keep `Documentation/zigux/README.md`,
`Documentation/zigux/review-checklist.md`,
`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`,
`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`,
`scripts/zigux/README.md`, `scripts\zigux/validate_phase11.zig`,
`zigux/Makefile`, and the returned `make -C zigux phase11-validate` route
explicit as the broader contributor-facing reminder family for the shared
Phase 11 packet, while `make -C zigux phase11` and
`make -C zigux phase11-contract` still remain missing on current `master`.
Keep those broader shared reminders adjacent to this note rather than turning
that contributor-facing packet into a driver-lane owner surface.

Current rereads in this run also keep the directly readable DesignWare
platform-registration, provenance, lane-gap, verify-alignment, checker,
registration-scaffold, the optional APB-clock scaffold outcomes, and adjacent
PM-helper packet through
`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
`Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
`Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
`scripts\zigux/check_phase11_dw_wdt_teardown_packet.zig`,
`scripts\zigux/check_phase11_dw_wdt_verify_alignment.zig`,
`zigux/tests/phase11_dw_wdt_manifest.json`,
`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
`drivers/watchdog/dw_wdt_pm.zig`, and
`drivers/watchdog/dw_wdt_pm_scaffold.zig` explicit as same-lane continuity
evidence beside the returned DesignWare matrix note, while
`drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and
`zigux/tests/phase11_dw_wdt.zig` stay explicit as repo-reality gaps instead of
current-head packet members, without promoting live PM execution, live MMIO
validation, or broader platform-backed registration into the shared packet.

Keep the returned gpio, bcm2835, and DesignWare validation matrices explicit as
shared matrix-boundary evidence while preserving bcm2835 and DesignWare deeper
owner-packet follow-through as separate continuity lanes.

HVC still has the smaller current-head continuity packet rather than the deeper
starter-depth replay or manifest stack, but that smaller packet now includes the
dedicated modem-control proof pair, the dedicated targetless-unregister witness
checker beside the standalone targetless-unregister witness pair, and the shared
three-proof inventory. bcm2835, gpio, and DesignWare reminder follow-through
still belong to their own lanes.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one driver lane at a time instead of batching bcm2835, gpio,
   DesignWare, and HVC work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane
   owns reminder-surface truthfulness, not driver-local execution claims.
3. Keep the current reread boundary honest: today that means the shared
   validation-matrix packet for
   `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
   `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
   `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
   `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, plus the adjacent
   `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`,
   `scripts\zigux/check_phase11_matrix_gap_survey.zig`,
   `scripts\zigux/check_phase11_validation_matrix_gap_survey.zig`,
   `scripts\zigux/check_phase11_build_inventory.zig`, the returned shared
   validator `scripts\zigux/validate_phase11.zig`, the directly readable
   DesignWare continuity packet through
   `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
   `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
   `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
   `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
   `scripts\zigux/check_phase11_dw_wdt_teardown_packet.zig`,
   `scripts\zigux/check_phase11_dw_wdt_verify_alignment.zig`,
   `zigux/tests/phase11_dw_wdt_manifest.json`,
   `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
   `drivers/watchdog/dw_wdt_pm.zig`, and
   `drivers/watchdog/dw_wdt_pm_scaffold.zig`, while
   `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and
   `zigux/tests/phase11_dw_wdt.zig` remain repo-reality-gap vocabulary in the
   returned DesignWare lane-gap note and matrix note, the returned archival
   `Documentation/zigux/phase11-shared-replay-contract.md`, and the HVC
   current-head continuity packet with its cleanup companion,
   `scripts\zigux/check_phase11_hvc_cleanup_current_head.zig`,
   `scripts\zigux/check_phase11_hvc_targetless_unregister_witness.zig`, shared
   build inventory anchor, proof-backed adjunct stack, dedicated modem-control
   proof pair, and standalone targetless-unregister witness pair; keep it
   explicit that the bcm2835 and DesignWare matrix notes now reread through
   this runtime's authenticated contents bridge alongside the gpio and HVC
   matrices, and that the returned shared replay contract does not by
   itself restore its older paired checker scripts or the missing
   `zigux/tests/phase11_build.zig` route.
4. Keep bcm2835 and DesignWare follow-through parked in their own lanes; do not
   widen either lane into live watchdog-core execution, PM plumbing, reset
   execution, IRQ execution, live MMIO validation, or claims of hardware-backed
   closure just because the shared packet can now name the returned driver-local
   matrix notes again.
5. Keep HVC current-head continuity and helper-local teardown or failure-mode
   evidence routed through `Documentation/zigux/phase11-hvc-console-survey.md`,
   `drivers/tty/hvc/hvc_console.zig`,
   `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
   `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,
   `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
   `scripts\zigux/check_phase11_hvc_cleanup_current_head.zig`,
   `scripts\zigux/check_phase11_hvc_targetless_unregister_witness.zig`,
   `zigux/tests/fixtures/phase11_build_inventory.json`,
   `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
   `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
   `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
   `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
   `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`,
   `zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
   `zigux/tests/phase11_hvc_modem_control_proof.zig`,
   `zigux/tests/phase11_hvc_modem_control_proof_build.zig`,
   `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, and
   `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`; do not widen
   that packet into tty registration, notifier execution, khvcd execution,
   sysrq dispatch, or host-backed teardown.
6. Do not imply broader platform registration, PM plumbing, reset execution,
   IRQ execution, MMIO validation, notifier execution, sysrq execution, khvcd
   execution, or hardware-backed closure beyond the helper, proof, note, and
   checker surfaces that were reread in this run.
7. When adjacent shared summaries or non-driver packets reopen elsewhere,
   mirror only the minimum driver-lane fact set they already prove; do not pull
   contributor-note or header-boundary ownership into this driver-only
   sequencing lane.
8. Keep the next bounded shared follow-through inside the smallest
   reminder-surface truthfulness repair unless a later reread restores or
   removes another Phase 11 packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the broader absent `make -C zigux phase11` and
  `make -C zigux phase11-contract` routes, the missing paired
  `scripts\zigux/check_phase11_shared_replay_contract.zig` and
  `scripts\zigux/check_phase11_shared_summary_surfaces.zig` routes, or the
  missing shared `zigux/tests/phase11_build.zig` replay family are already
  present on current `master` just because the returned archival
  `Documentation/zigux/phase11-shared-replay-contract.md`, the returned shared
  validator `scripts\zigux/validate_phase11.zig`, and the now-returned
  `make -C zigux phase11-validate` path are back
- a claim that bcm2835 or DesignWare broader reminder packets, helper stacks, or
  replay routes have all returned just because the driver-local validation
  matrices now reread directly on current `master`
- a claim that bcm2835 or gpio reminder packets have been broadly reread beyond
  the watchdog-local surfaces touched in their own lanes
- a claim that the older DesignWare packet-checker handle is already directly
  readable again
- broader hardware-backed watchdog validation, tty registration parity,
  notifier execution, sysrq dispatch, khvcd execution, or host-backed teardown
  closure
- a migration of driver-local reminder ownership into the shared packet
- a migration of contributor-note or header-boundary ownership into the
  driver-lane split
