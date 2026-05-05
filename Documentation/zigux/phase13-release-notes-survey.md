# Phase 13 Release Notes Survey

This note records the current shipped Phase 13 release-facing helper packet on `master`.

## Status

- `PHASE13_RELEASE_PACKET_STATUS=active`
- `PHASE13_SHARED_REPLAY_STEP_COUNT=7`
- shared replay files:
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
- validator-first route:
  - `scripts/zigux/validate-phase13-release.py`
  - `scripts/zigux/check-phase13-devres-packet.py`
  - `make -C zigux phase13-validate`
  - `make -C zigux phase13`

## Shared release packet

The current shipped Phase 13 helper packet stays validator-first and replay-backed.

The shared replay on `master` is now the seven-test bundle wired by `zigux/tests/phase13_build.zig`. That bundle covers the helper-first `libfs`, `devres`, `devres` reviewability, `devres` DMA-coherent boundary replay, `landlock/ruleset`, `landlock/syscalls`, and `libfs` reviewability anchors without adding extra replay steps for adjacent release evidence.

Inside that packet, the Phase 13 `devres` lane remains bounded to helper-only planning around `lib/devres.c`. The shipped `lib/devres.zig` lab and `zigux/tests/phase13_devres.zig` replay keep MMIO-adjacent behavior explicit for managed ioremap lifetime planning, `__devm_ioremap_resource()` sizing and failure shaping, `devm_of_iomap()` translated-resource planning, and WC memtype reservation bookkeeping while still blocking live MMIO, live device-tree walking, DMA-backed mapping, and live arch memtype mutation.

## Adjacent release evidence

These files are shipped adjacent release-surface evidence on `master`, but they do not add extra shared replay steps beyond the seven-test route above:

- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`

## Current blocker posture

The current Phase 13 packet does not claim closure.

It remains an active helper-first release packet while these boundaries stay explicit:

- `lib/devres.zig` does not claim live MMIO mappings or unmap side effects
- `lib/devres.zig` does not claim live OF tree walking or overlapping resource arbitration
- `lib/devres.zig` does not claim live DMA-backed mapping or scatterlist ownership
- `lib/devres.zig` does not claim live arch memtype state mutation
- the notifier surfaces remain adjacent release evidence rather than extra shared replay steps

## Replay commands

1. `python3 scripts/zigux/validate-phase13-release.py`
2. `python3 scripts/zigux/check-phase13-devres-packet.py`
3. `zig build test --build-file zigux/tests/phase13_build.zig --summary all`
4. `make -C zigux phase13`
