# Phase 11 UAPI Header Parity Survey
## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=adjacent_proof_shard_readback_only`
- lane: `P11-L02`
- reviewed against live `master` readback on `2026-05-21`
- scope: keep the Phase 11 public-header evidence truthful around the bounded HVC header boundary and the roadmap-backed watchdog/HVC review surface without widening into tty-core or watchdog-core ownership

## Current Repo Reality
- this note still ships on current `master` beside the adjacent current-head header-boundary packet:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `drivers/tty/hvc/hvc_console.h`
- the older shared header-packet companions named by earlier continuity still do not read back at their former paths on current `master`:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `zigux/tests/phase11_build.zig`
- current shared reminder and machine-checked HVC header-boundary evidence therefore still lives in the newer focused proof packet and its adjacent current-head companion stack:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `drivers/tty/hvc/hvc_console.h`
- that narrower proof packet remains `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` together with the dedicated exported-helper replay in `zigux/tests/phase11_hvc_export_surface_layout_build.zig`; those build routes keep the `hv_ops` and exported-surface proof shards tied to `zigux/helpers/layout_assert.zig` instead of relying on note-only or ad hoc offset claims.
- the returned `Documentation/zigux/phase11-shared-replay-contract.md` note is a reminder surface only in this lane: its presence shows that the shared Phase 11 reminder packet has rematerialized as documentation, but it does not by itself rematerialize the missing dedicated survey source, manifest, checker, or shared Phase 11 build route for cross-driver header parity.

## Roadmap Fit
- Phase 11 still treats bounded watchdog and HVC public surfaces as the simple-production-driver anchors.
- Phase 11 still requires reviewable validation and honest failure-mode evidence before expansion.
- Because the older shared header-survey manifest, checker, survey source, and shared build companion are still absent from current `master` even though the shared replay-contract note has returned, this note is truthful only if it records that the live repo now proves the HVC-side header boundary through focused proof shards, their build files, the adjacent validation matrix, the shared sequencing notes, the returned reminder contract note, and the surviving inventory stack rather than a restored shared replay route.
- The roadmap's ABI gate still expects explicit layout assertions and bounded proof, so the current packet should name the surviving `layout_assert`-backed HVC checkpoints directly instead of implying that the missing shared replay family already covers them.
- The roadmap still keeps watchdog and HVC surfaces in scope, so this note should not imply that the old shared `watchdog_info` replay remains live when the current accessible packet is narrower and HVC-centered.
- The broader shared ABI replay remains a real gap on current `master`: no directly readable shared survey source, manifest, checker, or shared Phase 11 build route currently rematerializes the older cross-driver packet.

## Current-Head Boundary
- `phase11-hvc-hv-ops-layout-proof-tests`: `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` still materializes the focused header-proof route, and `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` still proves `struct hv_ops` at size 72, alignment 8, with callback-table offsets 0 through 64 while tying each callback marker back to `drivers/tty/hvc/hvc_console.h` through the shared `layout_assert` helper substrate.
- `phase11-hvc-export-surface-layout-proof-tests`: `zigux/tests/phase11_hvc_export_surface_layout_build.zig` keeps the dedicated exported-helper replay directly readable, and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` keeps `struct winsize` explicit at size 8, alignment 2, with offsets 0, 2, 4, and 6; keeps the exported helper surface itself explicit as `HvcExportSurface` at size 72, alignment 8, with offsets 0 through 64 from `hvc_instantiate` through `notifier_hangup_irq`; keeps the helper signatures machine-checked through `notifier_hangup_irq`; and preserves the exported-surface ABI proof as a `layout_assert`-backed checkpoint instead of a prose-only reminder.
- `phase11-hvc-console-header-constant-assert`: `drivers/tty/hvc/hvc_console.h` still exposes `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` beside the `hv_ops` callback table and exported helper declarations.
- `phase11-build-inventory-adjunct`: `zigux/tests/fixtures/phase11_build_inventory.json` still points at the proof-backed adjunct packet, names `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` as the current adjunct build trio, records the exact `check-phase11-build-inventory.py` and `check-phase11-hvc-cleanup-current-head.py` readback commands, and keeps both dedicated survey replays and shared split replays empty instead of pretending the removed shared `zigux/tests/phase11_build.zig` route is live again.
- `phase11-shared-replay-contract-reminder`: `Documentation/zigux/phase11-shared-replay-contract.md` now rematerializes as a shared reminder note, but it should be read here only as documentation-level continuity evidence; it does not outweigh the still-missing dedicated survey source, manifest, checker, or shared Phase 11 build route that would be needed to claim a restored cross-driver header-parity replay packet.

## Why This Stays Bounded

- The current packet keeps real HVC header-boundary evidence reviewable on current `master`.
- It does not claim that the retired shared replay route, manifest, survey source, checker, or shared build route still ship.
- It keeps the roadmap-facing gap explicit: current `master` still lacks the broader shared ABI replay that used to carry cross-driver public-struct proof beyond the surviving HVC-centered `layout_assert` shards.
- It does not claim watchdog-core integration, tty registration parity, notifier execution parity, or whole-Phase-11 closure.
- Any future recovery of a broader shared header survey should first land as real repo files again before this note starts describing that route as live.
