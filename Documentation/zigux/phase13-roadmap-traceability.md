# Phase 13 Roadmap Traceability

This note keeps the roadmap-to-repo owner map truthful for the active Phase 13 shared-helper packet on current `master`.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche bounded to four Linux anchors:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

## Shared Reminder Surfaces

When shared Phase 13 wording changes, keep these reminder surfaces aligned first:
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

Keep `zigux/Makefile` distinct from the still-missing shared wrapper names `make -C zigux phase13-validate` and `make -C zigux phase13`.

## Anchor Map

Current `master` maps the four roadmap anchors to these bounded packet states:
- `fs/libfs.c`: bounded helper packet and reviewability work stay split between the shipped helper-local files and the still-missing `zigux/tests/phase13_libfs_addressability.zig` gap.
- `lib/devres.c`: bounded helper packet and planner families stay split between the shipped DMA, iomap, iounmap, and scatterlist files and the still-missing direct replay, reviewability, and manifest companions.
- `security/landlock/ruleset.c`: bounded helper packet stays mapped through `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, while the slice and ownership notes remain repo-reality gaps.
- `security/landlock/syscalls.c`: current `master` materializes the helper-local packet plus the direct reviewability companion through `security/landlock/syscalls.zig`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`. The direct replay companion `zigux/tests/phase13_landlock_syscalls.zig`, the manifest companion `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` route remain repo-reality gaps.

## Adjacent Evidence

Adjacent notifier evidence can support release-surface truthfulness, but it does not become a fifth roadmap anchor.

## Repo-Reality Gaps

Keep the remaining current gaps explicit:
- docs-root `Documentation/zigux/README.md` still lacks a dedicated Phase 13 reminder block
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `zigux/tests/phase13_landlock_syscalls.zig`
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
