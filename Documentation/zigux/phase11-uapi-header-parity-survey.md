# Phase 11 UAPI Header Parity Survey
## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_gap_reopened`
- lane: `P11-L18`
- reviewed against `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839` on current `master`
- scope: keep the Phase 11 public-header evidence truthful around the bounded HVC header boundary and the roadmap-backed watchdog/HVC review surface without widening into tty-core or watchdog-core ownership

## Current Repo Reality
- this note still ships on current `master`:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- the older shared header-packet companions named by earlier continuity no longer read back at their former paths on current `master`:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `zigux/tests/phase11_build.zig`
- current machine-checked HVC header-boundary evidence instead lives in the newer focused proof packet:
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `drivers/tty/hvc/hvc_console.h`

## Roadmap Fit
- Phase 11 still treats bounded watchdog and HVC public surfaces as the simple-production-driver anchors.
- Phase 11 still requires reviewable validation and honest failure-mode evidence before expansion.
- Because the older shared header-survey companions are gone from current `master`, this note is truthful only if it records that the live repo now proves the HVC-side header boundary through focused proof shards and cleanup-packet evidence rather than a restored shared replay route.
- The roadmap still keeps watchdog and HVC surfaces in scope, so this note should not imply that the old shared `watchdog_info` replay remains live when the current accessible packet is narrower and HVC-centered.

## Current-Head Boundary
- `phase11-hvc-hv-ops-layout-proof-tests`: `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` still proves `struct hv_ops` at size 72, alignment 8, with callback-table offsets 0 through 64, and ties each callback marker back to `drivers/tty/hvc/hvc_console.h`.
- `phase11-hvc-export-surface-layout-proof-tests`: the same focused build keeps `struct winsize` explicit at size 8, alignment 2, with offsets 0, 2, 4, and 6, and keeps the exported HVC helper declarations machine-checked through `notifier_hangup_irq`.
- `phase11-hvc-console-header-constant-assert`: `drivers/tty/hvc/hvc_console.h` still exposes `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` beside the `hv_ops` callback table and exported helper declarations.
- `phase11-build-inventory-adjunct`: `zigux/tests/fixtures/phase11_build_inventory.json` now points at `zigux/tests/phase11_hvc_cleanup_packet_build.zig` and lists the two header-proof modules plus the cleanup packet proof instead of a shared `zigux/tests/phase11_build.zig` route.
- `phase11-hvc-cleanup-packet-proof`: `zigux/tests/phase11_hvc_cleanup_packet_proof.zig` keeps the current-head HVC cleanup packet aligned with the survey, cleanup companion, validation matrix, verify-helper boundary note, and `drivers/tty/hvc/hvc_console.zig` helper summaries without pretending that the removed shared header packet still exists.

## Why This Stays Bounded

- The current packet keeps real HVC header-boundary evidence reviewable on current `master`.
- It does not claim that the retired shared replay route, manifest, survey source, checker, or replay contract still ship.
- It does not claim watchdog-core integration, tty registration parity, notifier execution parity, or whole-Phase-11 closure.
- Any future recovery of a broader shared header survey should first land as real repo files again before this note starts describing that route as live.
