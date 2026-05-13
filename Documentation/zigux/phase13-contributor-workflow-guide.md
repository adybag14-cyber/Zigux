# Phase 13 Contributor Workflow Guide

## Purpose

Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one compact contributor-facing workflow instead of scattered reminders.

This guide is for contributor workflow guidance only.
It does not create a new helper lane, a new replay count, or a new closure claim.

## Packet Boundary

Keep the current Phase 13 packet bounded to the roadmap-owned helper families:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Keep notifier evidence adjacent to that packet rather than treating it as a fifth helper anchor.
The adjacent notifier evidence packet is currently anchored through:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, and the Linux-side `drivers/tty/hvc/hvc_console.h` header.
If remaining direct notifier companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, or `zigux/helpers/hlist_view.zig` cannot be materialized on current `master`, record them as adjacent repo-reality gaps instead of as independently shipped review evidence.

## Shared Surfaces

When contributor-facing wording changes, keep these broad surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Treat `make -C zigux phase13-validate` as the stable contributor-facing replay handle.
If a direct `scripts/zigux/validate-phase13-release.py` or `scripts/zigux/check-phase13-*.py` path cannot be materialized on current `master`, record that gap as repo reality instead of presenting the missing script as independently shipped reviewer evidence.

## Current Repo Reality

As of `2026-05-13`, current `master` materializes the bounded `libfs` foothold through `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`. It also materializes the devres helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`. Current `master` also materializes the helper-local Landlock packet through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md` and `Documentation/zigux/phase13-landlock-ruleset-survey.md` notes, the shipped `security/landlock/ruleset.zig` starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, the shipped `Documentation/zigux/phase13-landlock-syscalls-slice.md` and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/syscalls.zig` starter, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` instead of treating Landlock as docs-only ownership metadata, but it still does not materialize these direct Phase 13 companions:
- `Documentation/zigux/phase13-libfs-slice.md`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_addressability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- older `scripts/zigux/check-phase13-devres-packet.py`

When a shared reminder or reviewer prompt still names any of those paths, treat that wording as contributor-guidance drift to repair instead of as shipped current-`master` evidence.
Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, but it still does not materialize these remaining direct notifier or list companions recorded in `Documentation/zigux/phase13-notifier-list-survey.md`, so shared contributor wording should keep them framed as adjacent repo-reality gaps rather than as independently shipped reviewer evidence:
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

## Workflow

1. Confirm the change stays inside one bounded Phase 13 lane.
2. Keep the owner split visible instead of collapsing `libfs`, `devres`, `landlock`, and notifier evidence into one generic summary.
3. If a broad reminder changes, reread the shared surfaces together before adding packet-local prose.
4. Before naming a direct scripts-root checker as review evidence, verify that the exact path is still present on current `master`; if it is not, keep the wording anchored to the shipped docs-root, tests-root, and `make -C zigux phase13-validate` surfaces and note the missing script as a blocker.
5. Before naming a direct helper-local tests-root companion as review evidence, verify that the exact path is still present on current `master`; if it is not, keep the wording anchored to the shipped docs-root, tests-root, and `make -C zigux phase13-validate` surfaces and note the missing direct companion as repo reality.
6. Before describing Landlock as docs-only ownership metadata, verify whether `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` are present on current `master`; if they are, keep those shipped helper anchors explicit while still recording the missing direct `zigux/tests/phase13_build.zig` and remaining notifier companions as repo reality.
7. Keep adjacent notifier evidence explicit whenever a contributor-facing summary mentions the shared Phase 13 packet.
8. Record Phase 13 as still active and reviewable; do not imply closure or a frozen packet.

## Contributor Prompts

Use these prompts when reviewing or updating shared workflow wording:
- Does the wording keep `libfs`, `devres`, `landlock`, and adjacent notifier evidence as separate ownership buckets?
- Does the wording keep the helper-owned Landlock ruleset boundary explicit through `Documentation/zigux/phase13-landlock-ruleset-ownership.md` instead of folding that owner cue into generic syscall or release wording?
- Does the wording keep the helper-owned Landlock syscalls governance and survey boundaries explicit through `Documentation/zigux/phase13-landlock-syscalls-governance.md` and `Documentation/zigux/phase13-landlock-syscalls-survey.md` instead of folding that owner cue into generic ruleset, notifier, or release wording?
- Does the wording keep the shipped helper-local `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `security/landlock/ruleset.zig`, and `security/landlock/syscalls.zig` starters, the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, and the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` explicit beside those ownership notes instead of treating Landlock as docs-only metadata?
- Does the wording keep notifier evidence adjacent to the shared-helper packet rather than counting it as a fifth helper tranche?
- Does the wording stay grounded in shipped contributor-facing notes instead of hoping for future validator or replay surfaces?
- Does the wording avoid presenting a direct `scripts/zigux/validate-phase13-release.py` or `scripts/zigux/check-phase13-*.py` path as independently shipped reviewer evidence when that exact file cannot be materialized on current `master`?
- Does the wording keep the currently missing direct `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and older `scripts/zigux/check-phase13-devres-packet.py` paths framed as repo-reality gaps instead of shipped evidence while leaving the shipped `Documentation/zigux/phase13-libfs-survey.md` note, the shipped `zigux/tests/phase13_libfs.zig` foothold, the shipped `zigux/tests/phase13_libfs_reviewability.zig` companion, the shipped `zigux/tests/phase13_libfs_manifest.json` survey packet, the shipped `Documentation/zigux/phase13-devres-slice.md` and `Documentation/zigux/phase13-devres-survey.md` notes, the shipped `zigux/tests/phase13_devres.zig` replay, the shipped `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json` companions, the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md` and `Documentation/zigux/phase13-landlock-ruleset-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the shipped `Documentation/zigux/phase13-landlock-syscalls-slice.md` and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json` direct ruleset replay pair, the shipped `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` direct syscall replay packet, the shipped `scripts/zigux/check-phase13-devres-packet-alignment.py` guard, and the shipped `scripts/zigux/check-phase13-landlock-ruleset-packet.py` guard explicit?
- Does the wording keep the landed nonincreasing-priority signal explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, and `make -C zigux phase13` while also keeping the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, and the Linux-side `drivers/tty/hvc/hvc_console.h` header explicit without counting them as extra shared replay steps, while leaving the remaining direct notifier or list companions framed as adjacent repo-reality gaps until current `master` materializes them?
- Does the wording keep the packet bounded to helper-first and truthfulness work instead of widening into subsystem-implementation claims?

## Non-Goals

- This guide does not claim a closed Phase 13 tranche.
- This guide does not promote notifier evidence into a fifth shared-helper anchor.
- This guide does not widen Phase 13 into runtime HVC parity, deeper security policy scope, or unrelated release-planning work.
