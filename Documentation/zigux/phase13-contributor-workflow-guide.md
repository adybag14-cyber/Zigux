# Phase 13 Contributor Workflow Guide

This guide keeps the current shipped Phase 13 shared-helper packet reviewable for contributors who are touching helper code, manifests, or the shared replay wiring.

## Scope

Use this guide when a change touches any part of the current shipped Phase 13 packet:
  * `fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json`
  * `lib/devres.c` through `zigux/tests/phase13_devres_manifest.json`
  * `security/landlock/ruleset.c` through `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `security/landlock/syscalls.c` through `zigux/tests/phase13_landlock_syscalls_manifest.json`

This is still an active helper-first tranche, not a globally closed roadmap phase.

## Keep In Sync

When a Phase 13 change is real, keep these surfaces aligned together:
  * contributor-facing docs: `Documentation/zigux/README.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and this guide
  * validator-first wiring: `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/README.md`, and `zigux/Makefile`
  * shared replay entrypoint: `zigux/tests/phase13_build.zig`
  * manifest-backed anchor packets: `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * direct replay files: `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_libfs_reviewability.zig`
  * adjacent shipped release-surface evidence: `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`

## Required Replay Order

Keep the validator-first release path explicit and unchanged unless the packet is being intentionally redesigned:

  1. `python3 scripts/zigux/validate-phase13-release.py`
  2. `make -C zigux phase13-validate`
  3. `zig build test --build-file zigux/tests/phase13_build.zig --summary all`
  4. `make -C zigux phase13`

The shared replay currently covers these seven tests:
  * `phase13-libfs-tests`
  * `phase13-devres-tests`
  * `phase13-devres-reviewability-tests`
  * `phase13-devres-dma-coherent-tests`
  * `phase13-landlock-ruleset-tests`
  * `phase13-landlock-syscalls-tests`
  * `phase13-libfs-reviewability-tests`

## Edit Patterns

### Anchor-local helper change

If you update one Phase 13 helper family:
  * update the owning Zig helper and its dedicated replay file first
  * update the owning manifest if the surveyed commit, blockers, checked focus, or release summary changed
  * refresh this guide and the shared checklist only when the contributor workflow or replay surface changed
  * keep the packet framed as the current four-anchor helper tranche unless the roadmap itself changes

### Shared release-packet change

If you update the shared release packet or convenience workflow:
  * keep this guide, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet.py`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned in the same change
  * keep the validator-first route explicit in every surface that names local replay commands
  * do not claim Phase 13 closure unless the shared replay and the remaining blocker posture both say the same thing

## Boundaries That Must Stay Explicit

Do not quietly erase these active Phase 13 limits from manifests, notes, or contributor guidance:
  * the current shared validator-first replay route covers only `libfs`, `devres`, `devres` reviewability, `devres_dma_coherent`, `landlock/ruleset`, `landlock/syscalls`, and `libfs` reviewability
  * the dedicated `devres` boundary checker remains part of the validator-first route through `scripts/zigux/check-phase13-devres-packet.py`
  * `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` are shipped adjacent release-surface evidence on `master`, but they do not add extra shared replay steps beyond the validator-first route above
  * the Phase 13 release packet stays active until the shared replay and the remaining blocker posture say otherwise together

## Fast Review Checklist

Before calling a Phase 13 change ready, confirm all of the following:
  * `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, the validator scripts, the build entrypoint, and the Make targets still name the same four manifest-backed anchors
  * `zigux/tests/phase13_build.zig` still exposes the same seven-test shared replay inventory or the contributor guidance explains the intentional change
  * the validator-first command order is unchanged across this guide, `scripts/zigux/README.md`, and `zigux/Makefile`
  * the change keeps the shipped release-notes, roadmap-traceability, and notifier evidence truthful without miscasting those files as extra replay steps or omitting them from the broader shared release surface
  * the change does not overstate runtime parity or global Phase 13 closure

## Next Safe Follow-up

The next contributor-facing improvement after this guide is to keep `Documentation/zigux/README.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` aligned with this guide whenever a future Phase 13 wording refresh changes the shared validator-first replay route or the broader shipped adjacent release-surface evidence.
