# Phase 11 UAPI Header Parity Validation Matrix

This document records the bounded current-head validation matrix for the Phase 11 shared header-boundary packet.

## Status

- `PHASE11_UAPI_HEADER_MATRIX_STATUS=adjacent_proof_shard_readback_only`
- lane: `P11-L02`
- reviewed against live `master`
- scope: keep the shared header-boundary reminder packet truthful using directly readable proof and note surfaces without overclaiming the still-missing shared replay manifest, survey source, or build route and without widening into tty-core or watchdog-core ownership
- current direct-readback packet:
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`
  - `Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  - `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
  - `zigux/helpers/layout_assert.zig`
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
  - `scripts/zigux/check-phase11-build-inventory.py`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
  - `drivers/tty/hvc/hvc_console.h`
  - `drivers/tty/hvc/hvc_console.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
- current direct contents reads in this lane do not rematerialize:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`

## Roadmap Anchor

- Phase 11 still treats straightforward watchdog and HVC surfaces as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.
- This matrix stays useful only if it reflects the smaller current-head packet that is directly readable today.

## Why This Exists

The lane-owned header-boundary matrix still matters, but current `master` no longer supports the older claim that the whole shared UAPI-header replay packet is directly readable and machine-checked through a returned survey source, manifest, checker, and shared build route.

What current `master` does still expose is a narrower adjacent packet: the matrix note, the survey note, the returned checker-coverage note, the returned `hv_ops` follow-up note, the older shared replay-contract reminder note, the shared sequencing notes that keep this packet separate from the driver-local HVC and watchdog lanes, the returned `zigux/helpers/layout_assert.zig` substrate, the HVC matrix that now records `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, and `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` as directly readable proof shards and build companions, the live `drivers/tty/hvc/hvc_console.zig` module that those focused proof builds import, the returned cleanup companion note, the returned verify-boundary note, the directly readable cleanup proof, modem-control proof, and targetless-unregister witness shards with their dedicated build companions, the surviving HVC-focused build inventory, its returned `scripts/zigux/check-phase11-build-inventory.py` checker route, the returned `scripts/zigux/check-phase11-hvc-cleanup-current-head.py` and `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` companion checker routes, the exported `drivers/tty/hvc/hvc_console.h` header surface, and the returned `scripts/zigux/check-phase11-header-boundary-packet.py` note-side checker route.

This matrix therefore records current-head truthfulness for that smaller adjacent packet instead of replaying the older shared-packet wording as if all of its direct anchors had returned.

## Current-Head Matrix

| lane surface | current evidence | bounded gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| exported-header proof shard | `zigux/helpers/layout_assert.zig`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `drivers/tty/hvc/hvc_console.h`, and `drivers/tty/hvc/hvc_console.zig` keep the bounded HVC exported-header shard directly readable through the shared ABI helper substrate, the live Zig module import path, `winsize` layout, `struct hv_ops` callback-table layout, and exported helper signature proof | the focused proof builds in `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` and `zigux/tests/phase11_hvc_export_surface_layout_build.zig` together with direct readback of the paired proof shards, the shared `layout_assert` helper, and the imported current-module surface keep the surviving public-header shard reviewable | if `hvc_console.h` grows or reorders the exported helper surface, `winsize`, or the callback table, or if `drivers/tty/hvc/hvc_console.zig` changes the imported ABI-facing shapes that those proof builds exact-check, refresh both proof shards and this matrix together in one bounded pass | notifier callback semantics, host-backed hypervisor transport, live tty registration, or broader HVC runtime behavior |
| adjacent HVC failure-mode companions | `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, `zigux/tests/phase11_hvc_modem_control_proof.zig`, `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` now keep the cleanup, modem-control, and targetless-unregister failure-mode companions directly readable beside the shared header-boundary reminder packet without turning them into a restored shared replay roster | direct reread of those companion notes, checkers, witness files, the focused modem-control proof pair, and the dedicated build routes keeps the adjacent failure-mode evidence honest beside the header-boundary shard packet | if the HVC companion stack adds or removes a cleanup, modem-control, or targetless-unregister checkpoint, refresh this matrix together with the survey note and the HVC validation matrix in the same bounded pass | treating cleanup, modem-control, or targetless-unregister adjacency as proof that the missing shared survey source, manifest, or build route has returned |
| header-boundary note stack | `Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`, `Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`, and `scripts/zigux/check-phase11-header-boundary-packet.py` now keep the returned note-side checker and the adjacent `hv_ops` proof distinction explicit inside the same current-head packet | direct reread of `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`, `python3 scripts/zigux/check-phase11-header-boundary-packet.py`, the returned checker-coverage note, and the returned `hv_ops` follow-up note keeps the four-note packet fail-closed without pretending that the missing shared replay family has returned | if the note-side packet grows or drops a same-lane continuity note, refresh the survey, matrix, companion note, and header-boundary checker in one bounded pass | treating the returned note-side checker as proof that the missing shared manifest, survey source, or build route have been restored |
| shared reminder posture | `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, the returned `Documentation/zigux/phase11-shared-replay-contract.md` reminder note, the returned `scripts/zigux/check-phase11-build-inventory.py` checker, the returned `scripts/zigux/check-phase11-hvc-cleanup-current-head.py` companion checker, the returned `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` witness checker, and the returned `scripts/zigux/check-phase11-header-boundary-packet.py` checker keep this matrix adjacent shared evidence rather than a driver-local HVC or watchdog lane member | direct reread of this matrix together with the sequencing, reminder-contract, matrix-gap, build-inventory checker, cleanup companion checker, targetless witness checker, and header-boundary checker routes keeps the lane split honest | refresh `Documentation/zigux/phase11-uapi-header-parity-survey.md`, the returned checker-coverage note, the returned `hv_ops` follow-up note, and the returned header-boundary checker only when the smaller surviving proof-shard packet changes again instead of the older shared replay family returning | folding this packet into `P11-L16`, the watchdog-local lanes, or broad contributor-note ownership |
| older shared replay family | `Documentation/zigux/phase11-shared-replay-contract.md` and `scripts/zigux/check-phase11-header-boundary-packet.py` now rematerialize as reminder-only continuity evidence, but current direct contents reads still do not rematerialize `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, or `zigux/tests/phase11_build.zig` | keep the returned header-boundary checker framed as note-side evidence only through `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test` and `python3 scripts/zigux/check-phase11-header-boundary-packet.py`, and keep the still-missing shared replay family explicit as repo-reality gaps until a future reread proves they returned | if any one of those shared packet anchors rematerializes, refresh this matrix in the same pass that restores the corresponding survey wording | claiming shared replay, manifest, survey-source, or build-route coverage as current-head evidence from historical wording alone |
| build inventory boundary | `zigux/tests/fixtures/phase11_build_inventory.json` and the returned `scripts/zigux/check-phase11-build-inventory.py` route are directly readable again, but their current body records the narrower HVC continuity packet rather than a returned header-boundary replay roster; that same narrower packet also keeps `zigux/tests/phase11_hvc_cleanup_packet_build.zig` inside the current adjunct build trio while leaving `zigux/tests/phase11_hvc_modem_control_proof_build.zig` and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` explicit as separate focused proof routes beside the inventory rather than inside it | direct reread of the inventory file together with `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`, `python3 scripts/zigux/check-phase11-build-inventory.py`, `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` is enough to keep this boundary explicit and fail-closed | add header-boundary inventory wording only when a directly readable shared replay file returns and needs to be tracked explicitly | using the HVC-only inventory or its adjacent witness routes as proof that the full shared header-boundary packet is landed again |
| focused direct-build replays | `scripts/zigux/check-phase11-focused-direct-build-replays.py`, `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `scripts/zigux/validate-phase11.py`, and `zigux/Makefile` keep the modem-control and targetless-unregister direct build replays explicit beside the narrower HVC continuity packet | direct reread of `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`, `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`, `scripts/zigux/validate-phase11.py`, `zigux/Makefile`, and the two focused build files keeps the current direct-build packet fail-closed | if the focused direct-build replays or their `validate-phase11.py` and `Makefile` wiring changes, refresh this matrix together with the survey note and the build-inventory packet in one bounded pass | using those focused direct builds as proof that the missing shared survey source, manifest, or shared build route returned |

## Review Rules

- Treat this matrix as current-head truthfulness for an adjacent shared header-boundary packet, not as proof that the older shared replay family is back on `master`.
- Do not use the returned exported-header proof shards, the returned build-inventory checker, the returned cleanup, modem-control, and targetless-unregister companion routes, the returned checker-coverage note, the returned `hv_ops` follow-up note, or the returned header-boundary checker to overclaim shared watchdog proof, a restored shared build route, checker coverage beyond the note-side packet, notifier execution, tty registration, watchdog-core integration, or whole-Phase-11 closure.
- Keep `Documentation/zigux/phase11-uapi-header-parity-survey.md` explicit as a readable note whose broader packet claims now need a same-lane refresh rather than as direct proof that the missing survey source, manifest, and shared replay route have already returned.
- Treat `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, and `scripts/zigux/check-phase11-header-boundary-packet.py` as returned reminder-only continuity evidence unless the missing shared replay files rematerialize beside them.
- Keep the adjacent cleanup, modem-control, and targetless-unregister companions explicit as directly readable HVC failure-mode continuity evidence without promoting them into shared header-parity replay coverage.
- If a future reread restores one or more of the missing shared packet anchors, update this matrix together with the survey note in the same bounded pass so the header-boundary packet stays reviewable without drift.
