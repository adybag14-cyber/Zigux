# Phase 13 Roadmap Traceability

This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.

It is a traceability document only. It does not create a new helper lane, a new replay route, or a tranche-closure claim.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.

The roadmap keeps that tranche bounded to four Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Keep the shared Phase 13 packet tied to those four anchors instead of collapsing it into a generic reminder surface or promoting adjacent notifier evidence into a fifth helper lane.

## Shared Packet Surfaces

This run directly reread these shared Phase 13 reminder surfaces on current `master`:

- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Keep the broader Makefile-backed and validator-first handle explicit as a repo-reality gap while current `master` still returns missing for `zigux/Makefile`, `scripts/zigux/validate-phase13-release.py`, and `zigux/tests/phase13_build.zig`. The current `.github/workflows/zigux-bootstrap.yml` readback no longer runs a dedicated Phase 13 route, so do not treat the workflow as a live shared Phase 13 replay surface.

## Anchor Map

Keep the roadmap-owned helper packet explicit through the exact anchor surfaces this run could verify directly:

- `libfs` remains a roadmap-owned anchor, but the direct helper-local packet is currently a repo-reality gap on current `master`: direct rereads returned missing for `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`.
- `devres` currently materializes through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, and `zigux/tests/phase13_devres_scatterlist_build.zig`. Keep the older direct helper packet explicit as a repo-reality gap here too because current rereads returned missing for `zigux/tests/phase13_devres_manifest.json` and `scripts/zigux/check-phase13-devres-packet.py`.
- `landlock/ruleset` currently materializes only through the surviving direct replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`. Keep the broader helper-local packet framed as a repo-reality gap because direct rereads returned missing for `security/landlock/ruleset.zig`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`.
- `landlock/syscalls` currently materializes only through `Documentation/zigux/phase13-landlock-syscalls-slice.md`. Keep the broader helper-local packet explicit as a repo-reality gap because direct rereads returned missing for `security/landlock/syscalls.zig`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`.

## Adjacent Evidence

Adjacent notifier evidence can still support release-surface truthfulness for the same Phase 13 packet, but it does not become a fifth roadmap anchor.

This run did not reopen notifier-local surfaces. Keep adjacent notifier evidence separate from the four-anchor map and require a fresh direct reread before promoting any notifier-side file back into the current Phase 13 traceability packet.

## Repo-Reality Gaps

Keep the exact missing shared-handle and anchor-local paths explicit until current `master` materializes them again:

- `zigux/Makefile`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/phase13_build.zig`
- `fs/libfs.zig`
- `Documentation/zigux/phase13-libfs-survey.md`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `scripts/zigux/check-phase13-devres-packet.py`
- `security/landlock/ruleset.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

Do not treat remembered lane notes, public fallback visibility, or manifest expectations as equivalent to a direct current-`master` contents read for any of those paths.

## Boundaries

- This note keeps the roadmap-to-repo map truthful for the active Phase 13 packet.
- This note does not widen Phase 13 into deeper subsystem implementation work.
- This note does not promote notifier evidence into a fifth helper anchor.
- This note does not treat missing helper-local or shared-build paths as shipped evidence.
- This note does not claim the Phase 13 tranche is closed.
