# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-subsystems packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it remains adjacent evidence rather than a fifth shared-helper anchor.

## Owner Split

Keep the current owner map explicit:

- `libfs` still owns the roadmap-backed `fs/libfs.c` anchor through `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, and `zigux/tests/phase13_libfs_manifest.json`, while `zigux/tests/phase13_libfs_addressability.zig` and the shared `zigux/tests/phase13_build.zig` route stay recorded as repo-reality gaps on current `master`; shared Phase 13 lanes must not reassert `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, or `zigux/tests/phase13_libfs_reviewability.zig` as stable current-`master` evidence unless the same run exact-rereads those three paths successfully, and any mismatch between the reminder packet and those direct reads stays parked for the helper-local `P13-Y01`, `P13-L03`, or `P13-L04` lanes instead of widening shared wording
- `devres` owns the currently readable DMA-boundary, `dmam_alloc_coherent()` planner, `iounmap` planner, `iomap` planner, survey, scatterlist-slice, scatterlist-planner, current-packet, and scatterlist helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, while `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay recorded as repo-reality gaps on current `master`
- `landlock/ruleset` keeps the shipped survey, helper starter, direct replay, manifest-backed packet, and dedicated checker explicit through `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, while `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, the shared `zigux/tests/phase13_build.zig` route, and broader tree plus hierarchy state stay recorded as repo-reality gaps on current `master`
- `landlock/syscalls` owns the narrower syscall governance, slice, helper-local survey packet, historical survey-gap breadcrumb, focused packet checker, helper starter, direct replay companion, and direct reviewability companion through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`
- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family

## Shared Packet Surfaces

Keep these shared reminder surfaces aligned when broad Phase 13 wording changes:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
- `python3 scripts/zigux/validate-phase13-release.py`

The shared reminder packet is aligned on current `master` for the shipped `libfs` slice, the returned `Documentation/zigux/phase13-libfs-survey.md`, and the still-missing addressability and shared-build-route companions. Direct `libfs` helper, direct replay, and reviewability claims stay helper-local: if exact current-`master` rereads for `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, and `zigux/tests/phase13_libfs_reviewability.zig` do not all succeed in the same run, shared Phase 13 reminder surfaces should defer that conflict back to the libfs-local lanes instead of restating the contested file list. Keep `python3 scripts/zigux/validate-phase13-release.py` explicit as shipped release-discipline support for that shared reminder set instead of leaving it implied behind the tests-root companion.

shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`

tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`

do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence

## Sequencing Rules

1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support, not as an extra shared replay step.
3. Use the shared-summary guard, the tests-root alignment companion, and the release-discipline validator before widening contributor wording across the packet.
4. Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.
5. Leave broader docs-root and tests-root refresh for a separate same-lane follow-up, and treat any future scripts-root or tests-root drift as a fresh reread task instead of carrying the already-cleared `libfs` README repair forward.
6. If a shared reminder surface starts treating the still-missing Landlock syscall manifest, shared build route, or live-state surfaces as shipped current-`master` evidence, correct that in this shared sequencing lane instead of reopening the syscall helper lanes.
7. If shared Phase 13 wording collides with an exact-read failure for `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, or `zigux/tests/phase13_libfs_reviewability.zig`, keep the conflict parked on the helper-local libfs lanes and update only the shared sequencing guidance needed to prevent overlap; do not use this lane to re-open libfs helper implementation, helper-local governance, or tests-root reminder work.

## Non-Goals

This note does not widen Phase 13 into:

- a direct filesystem parity claim beyond the roadmap-owned `libfs` anchor while its addressability and shared build-route companions still remain repo-reality gaps on current `master`
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock notes
- a claim that the Phase 13 packet is closed or frozen
