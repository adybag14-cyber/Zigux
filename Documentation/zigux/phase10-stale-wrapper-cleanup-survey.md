# Phase 10 Stale Wrapper Cleanup Survey

This survey records the current Phase 10 churn-control boundary for the virtio lab-driver lane. It is intentionally evidence-local: it does not add driver wrappers, transport behavior, or new validation routes.

## Current Repo Reality

- `scripts\zigux/validate_phase10.zig` is the shared Phase 10 gate and still requires the Phase 10 closure packet, core, ring, input, MMIO, harness, tests-root, closure-manifest, bootstrap-route, and freeze-boundary checkers.
- `Documentation/zigux/phase10-closure-evidence.md` still treats `scripts/zigux/README.md`, `scripts\zigux/check_phase10_core_packet.zig`, `scripts\zigux/check_phase10_closure_manifest_counts.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, and `zigux/Makefile` as current shared reminder evidence.
- `zigux/Makefile` still exposes the shared `phase10-validate`, `phase10-test`, and `phase10` route family, so Phase 10 is active repo reality rather than a historical wrapper-only packet.
- The current scripts-root reminder surface is a churn hotspot: recent readback emphasized other phase packets while older continuity still expected the Phase 10 shared checker roster there.

## Exact Evidence Readback

Current `master` readback on 2026-05-29 shows that the churn filter must not treat `scripts\zigux/check_phase10_core_packet.zig` as stale wrapper debt:

- `scripts\zigux/validate_phase10.zig` (`8e63b13ee69855937f94e4022d2f8287ca0abd23`) lists `scripts\zigux/check_phase10_core_packet.zig` in both `REQUIRED_PATHS` and the live `CHECKS` tuple as `phase10-core-packet`.
- `scripts\zigux/validate_phase10_closure.zig` (`f943e4e3fc233475e5666d1d5d7307f1550d06d0`) lists `scripts\zigux/check_phase10_core_packet.zig` in `REQUIRED_FILES`, keeps core-packet provenance markers in the closure evidence checks, and keeps the Phase 10 exact-check count at 15.
- `zigux/tests/phase10_closure_manifest.json` (`8f80348772cd6ebe5fd040e492c5947892cb5528`) includes `scripts\zigux/check_phase10_core_packet.zig` in `roadmap_parity_scoreboard.lab_only_driver_validation.evidence` and in `exact_checks` as `zig run scripts/zigux/check_phase10_core_packet.zig`.
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md` (`1bac327ecdbecdc6ed3f820f2097a12b0dce08f9`) records `PHASE10_LEDGER_CORE_PACKET_VALIDATE=scripts\zigux/check_phase10_core_packet.zig`, `PHASE10_LEDGER_REPO_REALITY_GAPS=none`, and the shared exact replay packet that includes `check-phase10-core-packet.py`.

Filter verdict: this lane should classify the core packet checker as current shared Phase 10 validation evidence. A future cleanup pass should only remove or demote it if all four surfaces above drop it together; otherwise, deleting it would be churn, not cleanup.

## Adjacent Wrapper-Generator Cross-Check

The adjacent Phase 3 wrapper cleanup route remains a separate filter family:

- `scripts/zigux/check_phase3_wrapper_templates.zig` (`ec4aad66b1bf058235e8d34fed411e9ca4f2fb3e`) detects wrapper-shaped `check-phase3-*.py` files with `is_generated_wrapper_script(...)`, accepting either exact generated stub text or the legacy `run_from_wrapper(__file__)` import-plus-call shape.
- `scripts\zigux/check_phase3_wrapper_templates.zig` (`326f3f8c6a796b1fbe57d316cf60ea87e64ed71c`) fail-closes that route by loading the generator and reporting every generated or legacy wrapper-shaped Phase 3 checker as `stale wrapper template: ...`.

That cross-check is useful evidence for stale-wrapper behavior, but it should not be used to reclassify the live Phase 10 core checker. Phase 10 closure evidence and Phase 3 wrapper-template retirement are adjacent churn-control lanes, not the same deletion target.

## Cleanup Boundary

- Keep Phase 10 cleanup bounded to truthfulness repairs around shipped checker and route surfaces.
- Do not generate new wrapper files only to make the tree larger.
- Do not promote risky transport, IRQ delivery, DMA behavior, remove lifecycle closure, or real input-device registration as complete from this lane.
- Treat `P10-L22` as the live owner for the bounded virtio-input packet; this `P10-L13` lane should only touch shared churn-cleanup evidence when it contradicts current repo reality.
- Treat Phase 3 wrapper-generator cleanup as adjacent evidence only unless a current Phase 10 surface directly depends on it.

## Hotspot Checklist

A future stale-wrapper cleanup pass should reread these files together before editing:

- `scripts/zigux/README.md`
- `scripts\zigux/validate_phase10.zig`
- `scripts\zigux/validate_phase10_closure.zig`
- `scripts\zigux/check_phase10_core_packet.zig`
- `scripts\zigux/check_phase10_closure_manifest_counts.zig`
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/Makefile`

## Next Bounded Step

If this survey needs follow-through, the safest next step is checker-local: teach an existing Phase 10 shared checker to fail when the scripts-root reminder loses the shipped Phase 10 checker roster. That should be done only after rereading current `master`, because broad whole-file writes to `scripts/zigux/README.md` have previously caused neighboring reminder-section churn.
