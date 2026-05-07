# Phase 13 Release Notes Survey

This note records the current shipped Phase 13 release-facing helper packet on `master`.

## Status
- `PHASE13_RELEASE_PACKET_STATUS=active`
- `PHASE13_SHARED_REPLAY_STEP_COUNT=8`
- shared replay files:
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `zigux/tests/phase13_devres_boundary_evidence.zig`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
- validator-first route:
  - `scripts/zigux/validate-phase13-release.py`
  - `scripts/zigux/check-phase13-devres-packet.py`
  - `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  - `scripts/zigux/check-phase13-notifier-packet.py`
  - `make -C zigux phase13-validate`
  - `zig build test --build-file zigux/tests/phase13_build.zig --summary all`
  - `make -C zigux phase13`

## Shared release packet

The current shipped Phase 13 helper packet stays validator-first and replay-backed.

The shared replay on `master` is now the eight-test bundle wired by `zigux/tests/phase13_build.zig`. That bundle covers the helper-first `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` anchors plus the bounded `devres` reviewability replay, the bounded `devres` DMA-coherent replay, the exact `devres` boundary-evidence replay, and the bounded `libfs` reviewability replay without turning the adjacent release evidence into extra shared replay steps.

The focused `zigux/tests/phase13_landlock_syscalls_reviewability.zig` shard is shipped direct helper evidence for the syscall anchor, but it stays outside that eight-test replay count so the release-facing packet does not quietly grow a ninth shared step.

Inside that packet, the Phase 13 `devres` lane remains bounded to helper-only planning around `lib/devres.c`.

The same validator-first release route on current `master` also reruns `scripts/zigux/check-phase13-landlock-ruleset-packet.py` and `scripts/zigux/check-phase13-notifier-packet.py` beside the shared release validator and the `devres` packet checker, so the helper-only ruleset blockers and adjacent notifier packet stay explicit without turning those dedicated guards into extra shared replay steps.

The shipped `lib/devres.zig` lab plus the paired `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_boundary_evidence.zig` replays keep MMIO-adjacent behavior explicit for managed ioremap lifetime planning, `__devm_ioremap_resource()` sizing and failure shaping, `devm_of_iomap()` translated-resource planning, coherent DMA reservation bookkeeping, WC memtype reservation bookkeeping, and the exact DMA-backed and scatterlist blocker evidence while still blocking live MMIO, live device-tree walking, DMA-backed mapping beyond the bounded coherent replay, scatterlist ownership, and live arch memtype mutation.

`Documentation/zigux/phase13-shared-helper-lane-sequencing.md` stays paired with that shipped release packet as the owner map for the active `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` helper families. It keeps the shared validator-first route, the eight-test build-backed replay, and the adjacent notifier evidence from collapsing into one ownerless Phase 13 surface just because those helpers now travel through the same release-facing packet on `master`.

## Adjacent release evidence

These files are shipped adjacent release-surface evidence on `master`, but they do not add extra shared replay steps beyond the eight-test route above:
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`

## Current blocker posture

The current Phase 13 packet does not claim closure.

It remains an active helper-first release packet while these boundaries stay explicit:
- `lib/devres.zig` does not claim live MMIO mappings or unmap side effects
- `lib/devres.zig` does not claim live device-tree walking or overlapping resource arbitration
- `lib/devres.zig` does not claim live DMA-backed mapping beyond the bounded coherent replay or scatterlist ownership
- `lib/devres.zig` does not claim live arch memtype state mutation
- the notifier survey, dedicated notifier packet checker, manifest, reviewability replay, and ABI-helper surfaces remain adjacent release evidence rather than extra shared replay steps

## Replay commands

1. `python3 scripts/zigux/validate-phase13-release.py`
2. `make -C zigux phase13-validate`
3. `zig build test --build-file zigux/tests/phase13_build.zig --summary all`
4. `make -C zigux phase13`
