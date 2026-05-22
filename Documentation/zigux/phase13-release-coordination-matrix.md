# Phase 13 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_RELEASE_CLOSED=no`
- shared-summary owner: `PMO / Release Management`
- workflow companion: `Documentation/zigux/phase13-contributor-workflow-guide.md`
- sequencing companion: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- release-notes companion: `Documentation/zigux/phase13-release-notes-survey.md`
- roadmap-traceability companion: `Documentation/zigux/phase13-roadmap-traceability.md`
- shared-summary-gap companion: `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- notifier-gap companion: `Documentation/zigux/phase13-notifier-summary-gap.md`
- shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
- release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`

Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.

## Active Shared Packet

Keep shared release wording tied to the four roadmap-owned Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.

## Owner Split

- PMO / Release Management: keep this matrix, the workflow guide, the sequencing note, the release-notes survey, the roadmap-traceability note, the shared-summary-gap note, the notifier-gap note, the shared-summary guard, the tests-root alignment companion, and the release-discipline validator aligned
- helper-local owners: keep `libfs`, `devres`, and `landlock` packet wording grounded in their shipped surveys, slices, starter files, focused reviewability manifests, and the narrower current `devres` packet's dedicated DMA-boundary checker pair, pure `dmam_alloc_coherent()` planner note plus manifest-backed replay, helper-first `devm_of_iomap()` planner note plus manifest-backed replay, helper-first `devm_iounmap()` planner note plus manifest-backed replay, and helper-first scatterlist build shard, while keeping the shipped Landlock syscalls governance-plus-slice-plus-starter packet explicit through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig` and leaving `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps
- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane

## Release Handle

Keep the stable contributor-facing handle distinct from this PMO coordination companion:

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `scripts/zigux/README.md`
3. `zigux/tests/README.md`

Keep these PMO coordination companions aligned beside that stable handle:

4. `Documentation/zigux/phase13-release-coordination-matrix.md`
5. `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
6. `Documentation/zigux/phase13-release-notes-survey.md`
7. `Documentation/zigux/phase13-roadmap-traceability.md`
8. `Documentation/zigux/phase13-shared-summary-guard-gap.md`
9. `Documentation/zigux/phase13-notifier-summary-gap.md`
10. `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
11. `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
12. `python3 scripts/zigux/validate-phase13-release.py`

That keeps the stable contributor-facing handle centered on the workflow guide, scripts-root reminder, and tests-root reminder while this matrix, the sequencing note, the release-note and roadmap-traceability companions, the two gap notes, and the three shipped validators stay explicit as coordination companions.

## Repo-Reality Gaps

Keep the still-missing Phase 13 route family recorded as repo-reality gaps rather than shipped current-`master` release support. `zigux/Makefile` itself is present again on current `master`, but it still does not expose the Phase 13 shared build handle.

- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`

Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support beside the shared-summary guard and tests-root alignment companion instead of carrying it in the repo-reality-gap bucket.

## Review Use

When shared Phase 13 wording changes:

1. reread this matrix beside the workflow guide, shared-helper sequencing note, release-notes survey, roadmap-traceability note, shared-summary-gap note, and notifier-gap note
2. rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
3. rerun `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` when the tests-root reminder packet changes or when shared wording could drift into `zigux/tests/README.md`
4. rerun `python3 scripts/zigux/validate-phase13-release.py` when the shared release packet changes so the PMO coordination note stays aligned with the shipped release-discipline validator
5. keep the Makefile-backed route family recorded as repo-reality gaps while distinguishing the returned `zigux/Makefile` file from the still-missing Phase 13 routes
6. leave broader README or tests-root packet refresh for a separate same-lane step when a fresh reread proves a new reminder-surface drift

## Next Coordinated Step

The recent docs-root, tests-root, and scripts-root Phase 13 `libfs` reminder repairs are now landed: current `master` keeps `scripts/zigux/README.md` aligned with the shipped `Documentation/zigux/phase13-libfs-slice.md` packet while `Documentation/zigux/phase13-libfs-survey.md` and `zigux/tests/phase13_libfs_addressability.zig` remain repo-reality gaps.

- reread `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` against `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` for the next smallest same-packet truthfulness or blocked-route wording drift instead of parking another scripts-root `libfs` follow-through that current `master` no longer needs
- keep the shipped tests-root alignment companion plus the focused adjacent notifier packet explicit when broader contributor-facing reminder surfaces refresh
- keep the shipped release-discipline validator explicit beside the shared-summary guard and tests-root alignment companion when the narrower `devres` DMA or scatterlist boundary packet is reread in future same-lane release-note cleanup
- keep the missing Phase 13 route family and the adjacent notifier follow-through parked as separate same-lane or helper-local work, while keeping the shipped Landlock syscalls governance-plus-slice-plus-starter packet explicit and the still-missing syscall survey-and-replay companions parked as separate repo-reality gaps

## Boundaries

- This matrix does not close the Phase 13 tranche.
- This matrix does not imply a shipped Makefile-backed review handle.
- This matrix does not promote adjacent notifier evidence into a fifth helper anchor.
