# Phase 13 Shared-Helper Lane Sequencing

This note keeps the active Phase 13 helper tranche from collapsing into one ownerless packet when nearby runs touch the same family on the same day.

## When to use it

Use this note when a change touches any of these active Phase 13 helper families:
  * `fs/libfs.zig`
  * `lib/devres.zig`
  * `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.zig`

This note matters most when the shared Phase 13 replay is already present on `master` and the next useful step could drift from helper-local work into packet-truthfulness wording, shared release-route churn, broader contributor-surface sync, or adjacent release-surface evidence.

## Shared packet surfaces that do not transfer ownership

These surfaces keep the current helper tranche reviewable, but they do not make one lane the owner of every nearby Phase 13 file:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/validate-phase13-release.py`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  * `scripts/zigux/check-phase13-notifier-packet.py`
  * `zigux/tests/phase13_build.zig`
  * `make -C zigux phase13-validate`
  * `make -C zigux phase13`

They coordinate the shared contributor-facing and validator-first packet, but they do not transfer helper-lane ownership across `libfs`, `devres`, `landlock/ruleset`, `landlock/syscalls`, or adjacent notifier evidence.

## Lane map

### `libfs` helper lane

Owns the direct `libfs` helper and its paired packet surfaces:
  * `fs/libfs.zig`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_addressability.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `Documentation/zigux/phase13-libfs-slice.md`
  * `Documentation/zigux/phase13-libfs-survey.md`

This lane should stay inside filesystem-helper delivery or packet-local truthfulness. It does not inherit ownership of `devres`, `landlock`, or notifier ABI work just because the shared Phase 13 build replays them together.

### `devres` helper-parity lane

Owns `lib/devres.zig` when the work is to add or validate direct helper behavior such as managed ioremap planners, wrapper entry points, memtype bookkeeping, or retained cleanup-token shaping.

That lane may update narrowly coupled direct helper checks, but it should not reopen the survey note, manifest, DMA-boundary replay, exact boundary-evidence replay, or checker wording unless the current packet would otherwise become false on `master`.

### `devres` packet-truthfulness lane

Owns the `devres` packet surfaces when the work is to keep the current Phase 13 story honest:
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `zigux/tests/phase13_devres_manifest.json`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `scripts/zigux/check-phase13-devres-packet.py`

This lane keeps the helper-only DMA, scatterlist, live-MMIO, and device-tree boundaries explicit. It does not own unpublished helper backlog inside `lib/devres.zig`.

### `landlock ruleset` helper lane

Owns the direct ruleset helper and its paired packet surfaces:
  * `security/landlock/ruleset.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

This lane should stay inside bounded ruleset-helper delivery or packet-local truthfulness. It does not absorb syscall-FD, path, `ruleset_fops`, or `landlock_restrict_self()` planning just because the shared Phase 13 replay already carries both Landlock anchors.

### `landlock syscalls` helper lane

Owns the direct syscall helper and its paired packet surfaces:
  * `security/landlock/syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`

This lane should stay inside bounded syscall-helper delivery or packet-local truthfulness. It does not absorb `security/landlock/ruleset.zig` tree-shaping, ownership, or blocker work just because nearby release notes and contributor prompts mention both Landlock anchors together.

Until `master` ships a dedicated `landlock syscalls` packet checker, treat `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` as the helper-local truthfulness trio that must move together whenever syscall-owned contributor wording, live-state limits, or owned-surface claims change.

When shared scripts-root or tests-root reminder text is refreshed, use that syscall-owned truthfulness trio as the shorthand for this lane rather than borrowing `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, which remains ruleset-lane evidence on `master`.

Broad contributor-facing reminders must also spell the split as `landlock/ruleset` and `landlock/syscalls` rather than collapsing both anchors into generic `landlock` shorthand.

### Adjacent notifier release-surface evidence

These surfaces remain adjacent release evidence:
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `scripts/zigux/check-phase13-notifier-packet.py`
  * `zigux/tests/phase13_notifier_list_manifest.json`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `include/zigux/abi.h`
  * `include/zigux/notifier_abi.h`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/list_view.zig`
  * `zigux/helpers/hlist_view.zig`
  * `zigux/helpers/notifier_chain_view.zig`

They stay reviewable beside the Phase 13 helper tranche, but they are not extra shared replay steps and they do not transfer notifier ownership into `libfs`, `devres`, `landlock/ruleset`, or `landlock/syscalls` lanes.

## Anti-overlap rules

1. If a run touches `lib/devres.zig`, decide first whether the work is helper parity or packet truthfulness. Do only one in the same run unless the packet would otherwise become false on current `master`.
2. If a run only refreshes manifests, survey notes, reviewability checks, checker wording, or shared contributor prompts, keep it out of helper backlog delivery.
3. If a run touches `security/landlock/`, decide first whether the work is ruleset-helper work or syscall-helper work. Do only one in the same run unless the owner map would otherwise become false on current `master`. Broad tests-root and scripts-root reminder refreshes still count as owner-map work here, so they must keep `landlock/ruleset` and `landlock/syscalls` separate instead of using one lane's checker as shorthand for the other.
4. Shared replay routes and shared contributor-facing surfaces may be updated when the packet shape really changes, but they do not justify widening from `libfs` into `devres`, from `devres` into `landlock`, from `landlock/ruleset` into `landlock/syscalls`, or from any shared-helper lane into notifier ABI evidence.
5. If nearby runs touch both Landlock anchors at once, the ruleset lane owns `security/landlock/ruleset.zig`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, and the dedicated ruleset packet checker; the syscall lane owns `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `Documentation/zigux/phase13-landlock-syscalls-governance.md` until the direct helper files stabilize again.

## Next safe follow-up

Reopen this note only if Phase 13 adds a new shared-helper family, promotes adjacent notifier evidence into the shared replay route, blurs the current `libfs` versus `devres` versus `landlock/ruleset` versus `landlock/syscalls` split again, or changes which broad contributor-facing surfaces must stay aligned around that packet.

On current `master`, the older docs-root, tests-root, and scripts-root Phase 13 follow-through steps named in earlier lane notes are already closed: `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now keep the helper-owned Landlock boundary notes and the adjacent notifier helper footholds explicit in their shared contributor-workflow wording.

The next safest contributor-guidance follow-up is to reread `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` together for the next one-surface wording drift while keeping the helper-owned Landlock notes and adjacent notifier evidence explicit.

Any future fail-closed guard for `Documentation/zigux/phase13-landlock-ruleset-ownership.md` or `Documentation/zigux/phase13-landlock-syscalls-governance.md` belongs in `scripts/zigux/validate-phase13-release.py` as tooling follow-through rather than as a cue to widen contributor-guidance work back into helper-local ownership or notifier packet scope.
