# Phase 11 UAPI Header Parity Survey
## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=adjacent_proof_shard_readback_only`
- lane: `P11-L02`
- reviewed against live `master` readback on `2026-05-25`
- scope: keep the Phase 11 public-header evidence truthful around the bounded HVC header boundary and the roadmap-backed watchdog/HVC review surface without widening into tty-core or watchdog-core ownership

## Current Repo Reality
- this note still ships on current `master` beside the adjacent current-head header-boundary packet:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
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
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `scripts/zigux/check-phase11-build-inventory.py`
  - `scripts/zigux/check-phase11-focused-direct-build-replays.py`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
  - `drivers/tty/hvc/hvc_console.h`
  - `drivers/tty/hvc/hvc_console.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
- the older shared header-packet companions named by earlier continuity still do not read back at their former paths on current `master`:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`
- current shared reminder and machine-checked HVC header-boundary evidence therefore still lives in the newer focused proof packet and its adjacent current-head companion stack:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  - `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
  - `zigux/helpers/layout_assert.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
  - `zigux/tests/phase11_hvc_modem_control_proof.zig`
  - `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
  - `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
  - `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `scripts/zigux/check-phase11-build-inventory.py`
  - `scripts/zigux/check-phase11-focused-direct-build-replays.py`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
  - `drivers/tty/hvc/hvc_console.h`
  - `drivers/tty/hvc/hvc_console.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
- that narrower proof packet remains `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` together with the dedicated exported-helper replay in `zigux/tests/phase11_hvc_export_surface_layout_build.zig`; those build routes keep the `hv_ops` and exported-surface proof shards tied to the returned `zigux/helpers/layout_assert.zig` substrate and the current `drivers/tty/hvc/hvc_console.zig` module instead of relying on note-only or ad hoc offset claims.
- the adjacent `scripts/zigux/check-phase11-build-inventory.py` route now keeps the current `zigux/tests/fixtures/phase11_build_inventory.json` packet fail-closed at the shared reminder layer, so the narrower HVC continuity roster is machine-checked evidence rather than unchecked inventory prose.
- the adjacent HVC failure-mode companion stack now also stays directly readable through `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, `zigux/tests/phase11_hvc_modem_control_proof.zig`, `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`; those cleanup, modem-control, and targetless-unregister routes are real current-head companion evidence beside the header-boundary shard packet, but they remain adjacent failure-mode continuity rather than a restored shared header-parity replay roster.
- the returned `Documentation/zigux/phase11-shared-replay-contract.md` note is a reminder surface only in this lane: its presence shows that the shared Phase 11 reminder packet has rematerialized as documentation, but it does not by itself rematerialize the missing dedicated survey source, manifest, or shared Phase 11 build route for cross-driver header parity.
- the returned `scripts/zigux/check-phase11-header-boundary-packet.py` route is also reminder-surface evidence only in this lane: it fail-closes on the note-side packet that current `master` still ships, but it does not by itself rematerialize the missing survey source, manifest, or shared build route that would be needed to claim a restored cross-driver header-parity replay packet.
- the current shared reminder surfaces outside this lane-owned note stack still under-report the live packet: `scripts/zigux/README.md` and `zigux/tests/README.md` currently jump from Phase 10 to Phase 12, so the directly readable scripts-root and tests-root packets still omit an explicit Phase 11 entry even though `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, `scripts/zigux/validate-phase11.py`, `zigux/Makefile`, and `make -C zigux phase11-validate` all ship on current `master`.

## Roadmap Fit
- Phase 11 still treats bounded watchdog and HVC public surfaces as the simple-production-driver anchors.
- Phase 11 still requires reviewable validation and honest failure-mode evidence before expansion.
- Because the older shared header-survey manifest, survey source, and shared build companion are still absent from current `master` even though the shared replay-contract note and the dedicated header-boundary checker have returned, this note is truthful only if it records that the live repo now proves the HVC-side header boundary through focused proof shards, their build files, the adjacent validation matrices, the shared sequencing notes, the returned reminder contract note, the returned `zigux/helpers/layout_assert.zig` substrate, the current `drivers/tty/hvc/hvc_console.zig` module readback, the returned build-inventory checker, the returned header-boundary checker, the adjacent cleanup and targetless-unregister companion packet, and the surviving inventory stack rather than a restored shared replay route.
- The roadmap's ABI gate still expects explicit layout assertions and bounded proof, so the current packet should name the surviving `layout_assert`-backed HVC checkpoints directly instead of implying that the missing shared replay family already covers them.
- The current note also needs to keep the newer bounded modem-control callback proof explicit beside cleanup and targetless-unregister continuity, because that focused ABI-facing proof is already landed on current `master` and belongs in the same honest failure-mode packet.
- The current note also needs to keep the returned `scripts/zigux/check-phase11-focused-direct-build-replays.py` route explicit beside the modem-control and targetless-unregister build pair, because that checker now keeps those ABI-facing proof routes fail-closed at the same current-head reminder layer.
- The roadmap still keeps watchdog and HVC surfaces in scope, so this note should not imply that the old shared `watchdog_info` replay remains live when the current accessible packet is narrower and HVC-centered.
- The broader shared ABI replay remains a real gap on current `master`: no directly readable shared survey source, manifest, or shared Phase 11 build route currently rematerializes the older cross-driver packet, and the returned header-boundary checker now only guards the narrower current-head note packet.
- The roadmap-facing truthfulness gap is slightly broader than the proof-shard gap alone: the shared scripts-root and tests-root reminder surfaces still skip Phase 11 even though the product roadmap keeps simple watchdog and HVC drivers in this tranche and the narrower header-boundary packet plus `phase11-validate` route are already directly readable on current `master`.

## Current-Head Boundary
- `phase11-hvc-hv-ops-layout-proof-tests`: `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` still materializes the focused header-proof route, `zigux/helpers/layout_assert.zig` still provides the shared ABI helper substrate for that route, and `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` still proves `struct hv_ops` at size 72, alignment 8, with callback-table offsets 0 through 64 while tying each callback marker back to `drivers/tty/hvc/hvc_console.h`.
- `phase11-hvc-export-surface-layout-proof-tests`: `zigux/tests/phase11_hvc_export_surface_layout_build.zig` keeps the dedicated exported-helper replay directly readable, `drivers/tty/hvc/hvc_console.zig` stays a direct proof input for that replay, `zigux/helpers/layout_assert.zig` still supplies the shared ABI helper substrate for that replay, and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` keeps imported `Winsize` and `HvOps` field types tied to that current module, keeps `struct winsize` explicit at size 8, alignment 2, with offsets 0, 2, 4, and 6; keeps the exported helper surface itself explicit as `HvcExportSurface` at size 72, alignment 8, with offsets 0 through 64 from `hvc_instantiate` through `notifier_hangup_irq`; keeps the helper signatures machine-checked through `notifier_hangup_irq`; and preserves the exported-surface ABI proof as a `layout_assert`-backed checkpoint instead of a prose-only reminder.
- `phase11-hvc-cleanup-companion`: `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, and `scripts/zigux/check-phase11-hvc-cleanup-current-head.py` now keep the returned cleanup and helper-boundary failure-mode companion explicit beside the shared build inventory and the HVC matrix, but they do not by themselves rematerialize the missing shared survey source, manifest, or shared Phase 11 build route.
- `phase11-hvc-modem-control-proof`: `zigux/tests/phase11_hvc_modem_control_proof.zig` and `zigux/tests/phase11_hvc_modem_control_proof_build.zig` keep the bounded `tiocmget`, `tiocmset`, `dtr_rts`, and `hupcl` teardown distinction explicit through the current `drivers/tty/hvc/hvc_console.zig` helper summaries without promoting the packet into live modem-control execution.
- `phase11-hvc-targetless-unregister-witness`: `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, and `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` now keep the standalone targetless-unregister witness explicit beside the narrower proof packet, but they remain focused failure-mode evidence rather than cross-driver header replay coverage.
- `phase11-hvc-console-header-constant-assert`: `drivers/tty/hvc/hvc_console.h` still exposes `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` beside the `hv_ops` callback table and exported helper declarations.
- `phase11-build-inventory-adjunct`: `zigux/tests/fixtures/phase11_build_inventory.json` still points at the proof-backed adjunct packet, names `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` as the current adjunct build trio, records the exact `check-phase11-build-inventory.py` and `check-phase11-hvc-cleanup-current-head.py` readback commands, keeps the adjacent `scripts/zigux/check-phase11-build-inventory.py` guard explicit as the current inventory-side review gate, and keeps both dedicated survey replays and shared split replays empty instead of pretending the removed shared `zigux/tests/phase11_build.zig` route is live again. The current exact-check bundle also keeps `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`, `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`, `zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`, and `zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` explicit beside that adjunct trio without recasting the inventory body itself as a broader shared replay roster.
- `phase11-shared-replay-contract-reminder`: `Documentation/zigux/phase11-shared-replay-contract.md` now rematerializes as a shared reminder note, but it should be read here only as documentation-level continuity evidence; it does not outweigh the still-missing dedicated survey source, manifest, or shared Phase 11 build route that would be needed to claim a restored cross-driver header-parity replay packet.
- `phase11-header-boundary-checker`: `scripts/zigux/check-phase11-header-boundary-packet.py` now fail-closes on the survey note and validation matrix through `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test` and `python3 scripts/zigux/check-phase11-header-boundary-packet.py`, but that returned checker should still be treated as note-side evidence only until a future reread proves the shared manifest, survey source, or build route returned beside it.
- `phase11-focused-direct-build-checker`: `scripts/zigux/check-phase11-focused-direct-build-replays.py` now keeps the current direct `zigux/tests/phase11_hvc_modem_control_proof_build.zig` and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` replays fail-closed beside the narrower build-inventory packet, so those focused build routes are machine-checked evidence rather than inventory-only prose.
- `phase11-shared-reminder-surface-gap`: `scripts/zigux/README.md` and `zigux/tests/README.md` still omit a Phase 11 packet entry, so the product-facing reminder surfaces remain one bounded step behind the live Phase 11 validator, HVC proof-shard packet, and roadmap-backed simple-driver tranche even though the lane-owned note stack is directly readable.

## Why This Stays Bounded

- The current packet keeps real HVC header-boundary evidence reviewable on current `master`.
- It now also records the adjacent cleanup, modem-control, and targetless-unregister companion routes as already-landed current-head continuity without promoting them into a restored shared replay roster.
- It now also records the remaining shared reminder-surface omission as part of the same roadmap-truthfulness gap, because the current scripts-root and tests-root packets still skip Phase 11 even though the narrower validator-backed packet is landed.
- It does not claim that the retired shared replay route, manifest, or survey source still ship.
- It keeps the roadmap-facing gap explicit: current `master` still lacks the broader shared ABI replay that used to carry cross-driver public-struct proof beyond the surviving HVC-centered `layout_assert` shards.
- It does not claim watchdog-core integration, tty registration parity, notifier execution parity, or whole-Phase-11 closure.
- Any future recovery of a broader shared header survey should first land as real repo files again before this note starts describing that route as live.
