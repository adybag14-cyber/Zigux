# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-subsystems packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:
- `fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json`
- `lib/devres.c` through `zigux/tests/phase13_devres_manifest.json`
- `security/landlock/ruleset.c` through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `security/landlock/syscalls.c` through `Documentation/zigux/phase13-landlock-syscalls-governance.md`

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it is still adjacent evidence rather than a fifth shared-helper anchor:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`

## Owner Split

Keep the current owner map explicit:
- `libfs` owns `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`
- `devres` helper parity owns `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`
- `devres` packet truthfulness owns `scripts/zigux/check-phase13-devres-packet.py` together with `zigux/tests/phase13_devres_boundary_evidence.zig`
- `landlock/ruleset` owns `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `landlock/syscalls` owns `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`
- adjacent notifier evidence owns `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h`

## Shared Packet Surfaces

When a real Phase 13 change lands, keep these shared surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/phase13_build.zig`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support for the shared packet, not as an extra shared replay step.
3. Keep the validator-first route explicit: `python3 scripts/zigux/validate-phase13-release.py`, then `make -C zigux phase13-validate`, then `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, then `make -C zigux phase13`.
4. If a broad reminder surface changes, keep the owner split visible instead of replacing it with a generic "Phase 13 helper packet" summary.
5. Do not imply a closed Phase 13 tranche or a fifth helper anchor while the packet still depends on bounded adjacent notifier evidence.

## Non-Goals

This note does not widen Phase 13 into:
- a direct filesystem parity claim beyond the shipped `libfs` packet
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock ruleset and syscall notes
- a claim that the Phase 13 packet is closed or frozen
