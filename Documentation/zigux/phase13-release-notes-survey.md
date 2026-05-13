# Phase 13 Release Notes Survey

## Purpose

This note keeps the contributor-facing release summary for the active Phase 13 shared-helper packet honest.

It is a release-surface note, not a new replay lane.

## What The Broad Release Summary Must Keep Visible

The current Phase 13 packet stays centered on four roadmap-owned helper families:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Broad summaries should keep the active shared-helper release handle visible through:
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

When current `master` cannot materialize direct helper-packet companions such as:
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`

broad summaries should record those paths as repo-reality gaps rather than independently shipped current-`master` evidence.

Broad summaries should also keep the paired Landlock ownership, ruleset-survey, syscall-governance, and syscall-survey notes explicit inside that same release handle through:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`

Broad summaries should keep those shipped Landlock helper anchors explicit instead of treating Landlock as docs-only ownership or governance metadata.

Broad summaries should also keep the shipped syscall-side helper packet explicit through:
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

Broad summaries should keep that shipped syscall helper packet explicit while still leaving the older shared `zigux/tests/phase13_build.zig` route framed as a repo-reality gap.

Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `zigux/tests/phase13_devres_manifest.json`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`

Broad summaries should also keep the current devres checker label explicit: older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift.

Broad summaries should also keep the currently materialized manifest-backed helper anchors explicit through:
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-roadmap-traceability.md`

Broad summaries should also keep the shipped adjacent notifier release surface visible through:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

If direct notifier companions such as:
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

cannot be materialized on current `master`, broad summaries should record them as repo-reality gaps rather than independently shipped current-`master` evidence.

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:
- the shared-helper packet is active rather than closed
- the validator-first release handle stays grounded in `Documentation/zigux/README.md`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`
- direct missing companions should stay recorded as repo-reality gaps until current `master` can materialize them again
- `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, the direct `zigux/tests/phase13_landlock_syscalls.zig` replay, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, the shipped `zigux/bindings/notifier_abi.zig`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, the shipped `include/zigux/abi.h` ABI foothold, the Linux-side `drivers/tty/hvc/hvc_console.h` header, and the shipped `security/landlock/ruleset.zig` plus `security/landlock/syscalls.zig` starters stay adjacent direct evidence rather than extra shared replay steps, while the older shared `zigux/tests/phase13_build.zig` route stays a repo-reality gap
- notifier evidence stays adjacent release-surface support rather than a fifth helper lane
- contributor-facing notes should prefer one bounded wording repair at a time
- broad summaries should stay grounded in the shipped docs packet rather than speculative future closure language
- adjacent notifier wording should keep the shipped `scripts/zigux/check-phase13-notifier-priority-signal.py` guard explicit and treat the older `scripts/zigux/check-phase13-notifier-packet.py` path as a repo-reality gap until current `master` materializes it again

## Where To Re-Read Before Updating Release Wording

Refresh these notes together when a contributor-facing Phase 13 summary changes:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase13-release.py`

## Non-Goals

- This note does not claim a new shared replay route.
- This note does not collapse the owner split into one generic Phase 13 helper bucket.
- This note does not claim HVC runtime parity or a broader notifier subsystem delivery.
