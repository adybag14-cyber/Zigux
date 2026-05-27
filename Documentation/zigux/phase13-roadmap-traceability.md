# Phase 13 Roadmap Traceability

This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche bounded to four Linux anchors:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

## Shared Reminder Surfaces

When shared Phase 13 wording changes, keep these reminder surfaces aligned first:
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/validate-phase13-release.py`

- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`

Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep `zigux/Makefile` distinct from the still-missing shared wrapper names `make -C zigux phase13-validate` and `make -C zigux phase13`.

Keep the stable contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` while the dedicated Phase 13 reminder block in `Documentation/zigux/README.md` stays aligned with that shared packet rather than being treated as a repo-reality gap.

## Anchor Map

Current `master` maps the four roadmap anchors to these bounded packet states:
- `fs/libfs.c`: bounded helper packet and reviewability work stay split between the shipped helper-local files and the still-missing `zigux/tests/phase13_libfs_addressability.zig` gap.
- `lib/devres.c`: bounded helper packet and planner families stay split between the shipped DMA, iomap, iounmap, and scatterlist files and the still-missing direct replay, reviewability, and manifest companions. Keep `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `zigux/tests/phase13_devres_scatterlist_planner_manifest.json` explicit as shipped current-`master` packet members while the older direct replay and manifest companions stay gap-only.
- `security/landlock/ruleset.c`: bounded helper packet stays mapped through `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, while the slice and ownership notes remain repo-reality gaps. Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning rather than widening it into full ruleset-state ownership.
- `security/landlock/syscalls.c`: keep the helper-local packet explicit through `security/landlock/syscalls.zig`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`; current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the older shared `zigux/tests/phase13_build.zig` companion, and the live file-descriptor installation, credential replacement, and ruleset-state surfaces stay repo-reality gaps on current `master`.

## Adjacent Evidence

Adjacent notifier evidence can support release-surface truthfulness, but it does not become a fifth roadmap anchor.

## Release Discipline

Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and missing notifier-chain companion.

## Repo-Reality Gaps

Keep the remaining current gaps explicit:
- keep the dedicated Phase 13 reminder block in `Documentation/zigux/README.md` aligned with the stable contributor-facing handle instead of treating docs-root coverage as missing again
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/helpers/notifier_chain_view.zig`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `include/zigux/notifier_abi.h`
- live `libfs` filesystem mutation and deeper VFS ownership
- live `devres` DMA, MMIO, scatterlist, and device-tree ownership
- live `landlock/ruleset` tree and hierarchy state
- live `landlock/syscalls` file-descriptor installation, credential replacement, ruleset-state ownership, and full syscall enforcement

## Boundaries

- This note keeps the roadmap-to-repo map truthful for the active Phase 13 packet.
- This note does not widen Phase 13 into deeper subsystem implementation work.
- This note does not promote adjacent evidence into a fifth helper anchor.
- This note does not claim the Phase 13 tranche is closed.
