# Phase 14 Attached Toolchain Guidance Gap

## Scope
- lane: `P14-L07`
- phase: `Phase 14`
- packet: shared validator-plus-guidance packet for the bounded Phase 14 smoke route
- status: `current-master reminder truthfulness follow-through`

## Why this note exists
The Phase 14 roadmap keeps the shared smoke packet in a study-only, reviewability-first posture. That means the shipped guidance needs to stay explicit about how reviewers reason about the attached Zig toolchain when it is the only available compiler, and this note needs to describe the current reminder split truthfully instead of replaying an older omission that current `master` has already closed.

## Current repo readback
Fresh rereads on 2026-05-19 show that the attached-toolchain reminder split is now more precise across the surviving shared reminder surfaces:
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keeps the attached-toolchain boundary explicit, but it no longer presents the older `phase14-*` wrapper examples as current usable fallback commands; instead it records those names only as historical packet-local rerun vocabulary while the readable `zigux/Makefile` body still lacks `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14`
- `Documentation/zigux/phase14-release-boundary-survey.md` now matches that narrower posture: it keeps the same older `phase14-*` wrapper names only as archival packet-local vocabulary and explicitly avoids restating the attached-toolchain triplet as current fallback guidance while the readable `zigux/Makefile` still omits those targets
- `scripts/zigux/README.md` mirrors the same three attached-toolchain wrapper examples in its Phase 14 block and keeps them framed as packet-local rerun vocabulary when `zig` is unavailable on `PATH`
- `zigux/tests/README.md` also keeps the attached-toolchain fallback explicit as packet-local rerun vocabulary rather than current build-backed evidence
- `scripts/zigux/validate-phase14.py` is directly readable again through the current contents path and now carries a real shared-smoke validator surface rather than the older placeholder-only body
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again through the current contents path and now keeps the release-facing exact-count posture aligned with the same reminder packet
- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` remain directly readable as the workqueue-local reviewability shard, so the attached-toolchain note should keep that returned study-only foothold explicit beside the reminder split

That means the older scripts-root omission recorded by this note is no longer the active same-lane gap on current `master`.

The remaining readback split is narrower:
- the reminder surfaces now keep the attached-toolchain boundary explicit, but only the scripts-root and tests-root reminders still spell out the older `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-*` examples directly, and both frame them as packet-local traceability vocabulary rather than active Makefile-backed fallback guidance
- the shared smoke note and release-boundary note now treat those same wrapper names as historical packet-local vocabulary instead of current fallback guidance, which better matches the readable `zigux/Makefile` route reality
- `zigux/Makefile` is readable again, and its live body currently exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes but no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets
- the broader executable packet still remains only partially recoverable in this lane even though the directly readable validator surface, the directly readable release-boundary guard, and the directly readable workqueue reviewability shard have returned

## Why this matters
This is still a real operational-truthfulness issue rather than a new delivery claim:
- the roadmap says Phase 14 stays bounded, study-only, and reviewability-first
- the bootstrap ledger favors exact rerun guidance over implied routes
- the attached toolchain is already part of the operating environment for bounded Zig validation
- the current reminder packet should now record the narrower split truthfully, so later same-lane work does not reopen a closed omission or re-promote the older wrapper names as active Makefile-backed proof by mistake

## Smallest honest same-lane conclusion
The attached-toolchain boundary itself is no longer the gap.

The active same-lane follow-through has narrowed to the broader shared-reminder split around recovered readback versus historical wrapper vocabulary:
1. keep `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, and `Documentation/zigux/phase14-shared-smoke-current-master-gap.md` aligned on the fact that the attached-toolchain boundary is still explicit, while only the scripts-root and tests-root reminders now spell out the older wrapper examples directly as packet-local traceability cues rather than active Makefile-backed fallback guidance
2. keep `zigux/Makefile` framed as readable current repo evidence that currently proves the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes rather than as returned proof of the older `phase14-*` routes
3. keep `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, the workqueue reviewability shard, `zigux/tests/phase14_build.zig`, and the other executable packet members framed according to the exact readback mode that is actually available in this lane

## Non-goals
- do not reopen workqueue, ring-buffer, skbuff, or RCU packet contents
- do not introduce a new Phase 14 replay route
- do not imply any live deep-core execution ownership or status change
- do not widen into Phase 15 freeze-map governance
