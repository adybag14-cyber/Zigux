# Phase 13 Contributor Workflow Guide

This guide keeps the active Phase 13 shared-helper packet reviewable for contributors who are touching helper code, manifests, release-facing notes, or the shared replay wiring.
## Scope

Use this guide when a change touches any part of the current Phase 13 packet:
  * `fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json`
  * `lib/devres.c` through `zigux/tests/phase13_devres_manifest.json`
  * `security/landlock/ruleset.c` through `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `security/landlock/syscalls.c` through `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * the adjacent notifier-list reviewability packet through `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig`
This is still an active helper-first tranche, not a globally closed roadmap phase.
## Keep In Sync

When a Phase 13 change is real, keep these surfaces aligned together:
  * release-facing docs: `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, and the packet-local `Documentation/zigux/phase13-devres-survey.md` boundary note
  * contributor-facing docs: `Documentation/zigux/review-checklist.md` and this guide
  * validator-first wiring: `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
  * shared replay entrypoint: `zigux/tests/phase13_build.zig`
  * manifest-backed anchor packets: `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * adjacent notifier packet: `zigux/tests/phase13_notifier_list_manifest.json` and `Documentation/zigux/phase13-notifier-list-survey.md`
## Required Replay Order

Keep the validator-first release path explicit and unchanged unless the packet is being intentionally redesigned:

  1. `python3 scripts/zigux/validate-phase13-release.py`
  2. `make -C zigux phase13-validate`
  3. `zig build test --build-file zigux/tests/phase13_build.zig --summary all`
  4. `make -C zigux phase13`

The shared replay currently covers these fourteen steps:
  * `phase13-libfs-tests`
  * `phase13-devres-tests`
  * `phase13-devres-dma-coherent-tests`
  * `phase13-devres-iounmap-reviewability-tests`
  * `phase13-devres-iomap-reviewability-tests`
  * `phase13-landlock-ruleset-tests`
  * `phase13-landlock-ruleset-reviewability-tests`
  * `phase13-landlock-syscalls-tests`
  * `phase13-landlock-syscalls-reviewability-tests`
  * `phase13-libfs-reviewability-tests`
  * `phase13-devres-reviewability-tests`
  * `phase13-devres-wrapper-reviewability-tests`
  * `phase13-notifier-list-reviewability-tests`
  * `phase13-notifier-chain-view-tests`
## Edit Patterns

### Anchor-local helper change

If you update one Phase 13 helper family:

  * update the owning Zig helper and its dedicated replay file first
  * update the owning manifest if the surveyed commit, blockers, checked focus, or release summary changed
  * refresh the release-facing note only when the shared packet meaning changed, not just because code moved internally
  * keep the packet framed as one of the four roadmap anchors unless the roadmap itself changes
### Shared release-packet change

If you update the release-facing packet or convenience workflow:
  * keep `Documentation/zigux/phase13-release-notes-survey.md`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned in the same change
  * keep the validator-first route explicit in every surface that names local replay commands
  * do not claim Phase 13 closure unless the shared replay, the release note, and the remaining blocker posture all say the same thing
### Notifier packet change

If you touch the notifier-list packet:

  * keep it visible as roadmap-adjacent release evidence, not a fifth roadmap anchor
  * keep the packet bounded to read-only notifier shape reviewability through `zigux/bindings/notifier_abi.zig` and `zigux/helpers/notifier_chain_view.zig`
  * keep notifier registration, callback execution, SRCU, and blocking-notifier semantics explicitly out of scope
## Boundaries That Must Stay Explicit

Do not quietly erase these active Phase 13 limits from manifests, notes, or contributor guidance:
  * `devres` still blocks live DMA-backed mappings and scatterlist ownership even though the coherent DMA bookkeeping replay is part of the shared build
  * `landlock/ruleset` still blocks `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown
  * the notifier-list packet is release evidence only for a read-only generic notifier foothold, not runtime notifier execution parity
  * the Phase 13 release packet stays active until the shared replay and the remaining blocker posture say otherwise together
## Fast Review Checklist

Before calling a Phase 13 change ready, confirm all of the following:
  * the packet still names exactly four roadmap anchors
  * the notifier packet still reads as adjacent evidence rather than a fifth anchor
  * the validator-first command order is unchanged across docs, script guidance, and Make targets
  * `zigux/tests/phase13_build.zig` still exposes the same shared replay inventory or the release note explains the intentional change
  * the blocker language for `devres`, `landlock/ruleset`, and notifier execution still matches the manifests and release note
  * the change does not overstate runtime parity, DMA ownership, or global Phase 13 closure
## Next Safe Follow-up

The next contributor-facing improvement after this guide is to wire the same Phase 13 workflow summary into the tests-root README so the tests surface, release note, and scripts guide all teach the same validator-first handoff.
