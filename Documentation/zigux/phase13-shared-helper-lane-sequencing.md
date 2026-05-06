# Phase 13 Shared-Helper Lane Sequencing

This note keeps the active Phase 13 helper tranche from collapsing into one ownerless packet when nearby runs touch the same family on the same day.

## When to use it

Use this note when a change touches any of these active Phase 13 helper families:
  * `fs/libfs.zig`
  * `lib/devres.zig`
  * `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.zig`

This note matters most when the shared Phase 13 replay is already present on `master` and the next useful step could drift from helper-local work into packet-truthfulness wording, shared release-route churn, or adjacent release-surface evidence.

## Shared packet surfaces that do not transfer ownership

These surfaces keep the current helper tranche reviewable, but they do not make one lane the owner of every nearby Phase 13 file:
  * `scripts/zigux/validate-phase13-release.py`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `zigux/tests/phase13_build.zig`
  * `make -C zigux phase13-validate`
  * `make -C zigux phase13`
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`

## Lane map

### `libfs` helper lane

Owns the direct `libfs` helper and its paired packet surfaces:
  * `fs/libfs.zig`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `Documentation/zigux/phase13-libfs-slice.md`
  * `Documentation/zigux/phase13-libfs-survey.md`

This lane should stay inside filesystem-helper delivery or packet-local truthfulness. It does not inherit ownership of `devres`, `landlock`, or notifier ABI work just because the shared Phase 13 build replays them together.

### `devres` helper-parity lane

Owns `lib/devres.zig` when the work is to add or validate direct helper behavior such as managed ioremap planners, wrapper entry points, memtype bookkeeping, or retained cleanup-token shaping.

That lane may update narrowly coupled direct helper checks, but it should not reopen the survey note, manifest, DMA-boundary replay, or checker wording unless the current packet would otherwise become false on `master`.

### `devres` packet-truthfulness lane

Owns the `devres` packet surfaces when the work is to keep the current Phase 13 story honest:
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_manifest.json`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `scripts/zigux/check-phase13-devres-packet.py`

This lane keeps the helper-only DMA, scatterlist, live-MMIO, and device-tree boundaries explicit. It does not own unpublished helper backlog inside `lib/devres.zig`.

### `landlock` helper lanes

Own the direct helper and packet surfaces under:
  * `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`

These lanes should stay inside bounded security-helper delivery or packet-local truthfulness. They do not absorb `libfs` or `devres` cleanup because the shared Phase 13 replay route already exists.

### Adjacent notifier release-surface evidence

These surfaces remain adjacent release evidence:
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `zigux/tests/phase13_notifier_list_manifest.json`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `include/zigux/notifier_abi.h`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/notifier_chain_view.zig`

They stay reviewable beside the Phase 13 helper tranche, but they are not extra shared replay steps and they do not transfer notifier ownership into `libfs`, `devres`, or `landlock` lanes.

## Anti-overlap rules

1. If a run touches `lib/devres.zig`, decide first whether the work is helper parity or packet truthfulness. Do only one in the same run unless the packet would otherwise become false on current `master`.
2. If a run only refreshes manifests, survey notes, reviewability checks, or checker wording, keep it out of helper backlog delivery.
3. Shared replay routes may be updated when the packet shape really changes, but they do not justify widening from `libfs` into `devres`, from `devres` into `landlock`, or from any shared-helper lane into notifier ABI evidence.
4. If two nearby runs touch `devres` at once, the helper-parity lane owns `lib/devres.zig`; the packet-truthfulness lane narrows to survey, manifest, reviewability, DMA-boundary, and checker surfaces until the helper file stabilizes again.

## Next safe follow-up

Reopen this note only if Phase 13 adds a new shared-helper family, promotes adjacent notifier evidence into the shared replay route, or blurs the current `libfs` versus `devres` versus `landlock` split again.
