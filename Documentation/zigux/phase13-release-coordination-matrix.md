# Phase 13 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_RELEASE_CLOSED=no`
- shared-summary owner: `PMO / Release Management`
- workflow companion: `Documentation/zigux/phase13-contributor-workflow-guide.md`
- sequencing companion: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- phase12 handoff companion: `Documentation/zigux/phase12-phase13-release-handoff.md`
- release-packet index companion: `Documentation/zigux/phase13-release-packet-index.md`
- release-notes companion: `Documentation/zigux/phase13-release-notes-survey.md`
- roadmap-traceability companion: `Documentation/zigux/phase13-roadmap-traceability.md`
- roadmap-traceability guard: `zig run scripts/zigux/check_phase13_roadmap_traceability.zig`
- shared-summary-gap companion: `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- notifier-gap companion: `Documentation/zigux/phase13-notifier-summary-gap.md`
- shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig`
- tests-root alignment companion: `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig`
- release-discipline validator: `zig run scripts/zigux/validate_phase13_release.zig`

Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.

## Active Shared Packet

Keep shared release wording tied to the four roadmap-owned Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts\zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.

## Owner Split

- PMO / Release Management: keep this matrix, `Documentation/zigux/phase13-release-packet-index.md`, the workflow guide, the sequencing note, `Documentation/zigux/phase12-phase13-release-handoff.md`, the release-notes survey, the roadmap-traceability note, the roadmap-traceability guard, the shared-summary-gap note, the notifier-gap note, the shared-summary guard, the tests-root alignment companion, and the release-discipline validator aligned so the downstream shared-helper packet stays contributor-facing and truthful without pretending the missing Phase 13 shared build handle has returned.
- helper-local owners: keep `libfs`, `devres`, and `landlock` packet wording grounded in their shipped surveys, slices, starter files, focused reviewability manifests, and the narrower current `devres` packet's dedicated DMA-boundary checker pair, pure `dmam_alloc_coherent()` planner note plus `scripts\zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig` and manifest-backed replay, the dedicated `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig` shard, helper-first `devm_of_iomap()` planner note plus manifest-backed replay, helper-first `devm_iounmap()` planner note plus manifest-backed replay, the shipped `scripts\zigux/check_phase13_devres_current_packet.zig` current-packet checker, helper-first scatterlist build shard, and the helper-local arch-WC release-record plus detach-cleanup follow-through now shipped in `lib/devres.zig` through `planManagedArchPhysWcAdd(...)` and `planManagedArchPhysWcDetachCleanup(...)`, while keeping the shipped Landlock syscalls governance, slice, survey, survey-gap breadcrumb, checker, starter packet, direct replay companion, and direct reviewability companion explicit through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts\zigux/check_phase13_landlock_syscalls_packet.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` and leaving `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as a repo-reality gap beside the shared `zigux/tests/phase13_build.zig` route and the live file-descriptor installation, credential replacement, and ruleset-state surfaces
- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts\zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane

## Release Handle

Keep the stable contributor-facing handle distinct from this PMO coordination companion:

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `scripts/zigux/README.md`
3. `zigux/tests/README.md`

Keep these PMO coordination companions aligned beside that stable handle:

4. `Documentation/zigux/phase13-release-packet-index.md`
5. `Documentation/zigux/phase13-release-coordination-matrix.md`
6. `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
7. `Documentation/zigux/phase12-phase13-release-handoff.md`
8. `Documentation/zigux/phase13-release-notes-survey.md`
9. `Documentation/zigux/phase13-roadmap-traceability.md`
10. `zig run scripts/zigux/check_phase13_roadmap_traceability.zig`
11. `Documentation/zigux/phase13-shared-summary-guard-gap.md`
12. `Documentation/zigux/phase13-notifier-summary-gap.md`
13. `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig`
14. `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig`
15. `zig run scripts/zigux/validate_phase13_release.zig`

That keeps the stable contributor-facing handle centered on the workflow guide, scripts-root reminder, and tests-root reminder while the packet index, this matrix, the sequencing note, the cross-phase handoff note, the release-note and roadmap-traceability companions, the dedicated roadmap-traceability guard, the two gap notes, and the three shipped validators stay explicit as coordination companions.

## Repo-Reality Gaps

Keep the still-missing Phase 13 route family recorded as repo-reality gaps rather than shipped current-`master` release support. `zigux/Makefile` itself is present again on current `master`, but it still does not expose the Phase 13 shared build handle.

- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `scripts\zigux/check_phase13_devres_packet_alignment.zig`
- `scripts\zigux/check_phase13_notifier_priority_signal.zig`

Current `master` now materializes `scripts\zigux/validate_phase13_release.zig` and `scripts\zigux/check_phase13_landlock_ruleset_packet.zig`, so keep those validators explicit as shipped release-discipline and helper-local support beside the shared-summary guard, the roadmap-traceability guard, and the tests-root alignment companion instead of carrying them in the repo-reality-gap bucket.

## Review Use

When shared Phase 13 wording changes:

1. reread this matrix beside `Documentation/zigux/phase13-release-packet-index.md`, the workflow guide, shared-helper sequencing note, `Documentation/zigux/phase12-phase13-release-handoff.md`, release-notes survey, roadmap-traceability note, shared-summary-gap note, and notifier-gap note
2. rerun `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig`
3. rerun `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig` when the tests-root reminder packet changes or when shared wording could drift into `zigux/tests/README.md`
4. rerun `zig run scripts/zigux/check_phase13_roadmap_traceability.zig` when roadmap-facing release wording, the four-anchor owner map, or the packet's shared helper split changes
5. rerun `zig run scripts/zigux/validate_phase13_release.zig` when the shared release packet changes so the PMO coordination note stays aligned with the shipped release-discipline validator
6. keep the Makefile-backed route family recorded as repo-reality gaps while distinguishing the returned `zigux/Makefile` file from the still-missing Phase 13 routes
7. leave broader docs-root or tests-root reminder refresh for a separate same-lane step, and when the narrower `devres` packet is what moved, anchor that follow-through to the shipped `dmam_alloc_coherent()` planner checker, `devm_of_iomap()` and `devm_iounmap()` planner notes, checker scripts, manifest-backed replays, the shipped `scripts\zigux/check_phase13_devres_current_packet.zig` current-packet checker, the helper-local `planManagedArchPhysWcAdd(...)` and `planManagedArchPhysWcDetachCleanup(...)` follow-through in `lib/devres.zig`, and the dedicated `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig` shard instead of restating the older direct `zigux/tests/phase13_devres.zig` family

## Next Coordinated Step

Current same-lane rereads now show the docs-root Phase 13 reminder block is aligned on current `master` beside the stable contributor-facing handle, the new packet index, the cross-phase handoff note, the four roadmap anchors, the helper-local `libfs`, `devres`, and `landlock` split, the adjacent notifier evidence, the shipped roadmap-traceability guard, and the still-missing `make -C zigux phase13-validate` plus `make -C zigux phase13` route names as repo-reality gaps.

- leave the docs-root Phase 13 reminder packet parked unless `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase12-phase13-release-handoff.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `scripts\zigux/check_phase13_roadmap_traceability.zig`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` drifts again
- if one of those shared reminder surfaces moves, reread the same packet first and land only the smallest reminder-side truthfulness repair, then rerun `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig`, `zig run scripts/zigux/check_phase13_roadmap_traceability.zig`, and `zig run scripts/zigux/validate_phase13_release.zig`
- keep the shipped `devres` planner-expanded reminder packet explicit whenever a shared reminder note summarizes existing work: `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `scripts\zigux/check_phase13_devres_iomap_planner.zig`, `scripts\zigux/check_phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `scripts\zigux/check_phase13_devres_current_packet.zig`, and `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, alongside the shipped DMA-boundary, `dmam_alloc_coherent()` planner-checker, scatterlist evidence, and the helper-local arch-WC add-plus-detach cleanup follow-through already carried in `lib/devres.zig`
- keep the missing Phase 13 route family, the adjacent notifier follow-through, and the still-missing Landlock syscall manifest plus shared-build-route companions parked as separate same-lane or helper-local work instead of reopening this PMO matrix for broader packet expansion by default

## Boundaries

- This matrix does not close the Phase 13 tranche.
- This matrix does not imply a shipped Makefile-backed review handle.
- This matrix does not promote adjacent notifier evidence into a fifth helper anchor.