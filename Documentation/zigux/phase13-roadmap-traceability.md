# Phase 13 Roadmap Traceability

## Purpose

This note maps the active Phase 13 contributor-facing packet back to the Zigux roadmap so broad reminder surfaces can stay tied to the real product lane.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.
The active contributor-facing packet stays inside that helper-first scope by keeping attention on:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence supports the same Phase 13 packet, but it remains adjacent evidence rather than a fifth roadmap anchor.
That adjacent evidence packet should stay explicit through:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only traversal helper `zigux/helpers/notifier_chain_view.zig`, and the Linux-side notifier header `drivers/tty/hvc/hvc_console.h`, so keep those paths explicit without counting them as extra shared replay steps.

Current `master` also materializes four manifest-backed helper anchors that keep the roadmap packet concrete even while the older shared build bundle stays absent:
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

Keep those four manifests explicit as the currently materialized helper-anchor set, while `zigux/tests/phase13_build.zig` stays framed as a repo-reality gap until current `master` materializes it again.

If direct notifier companions such as `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, or `zigux/helpers/hlist_view.zig` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped evidence.

## Traceability Map

- `libfs` maps to the bounded shared-helper tranche and should stay represented as its own contributor-facing bucket through the shipped `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json` while older direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, and `zigux/tests/phase13_libfs_addressability.zig` stay framed as repo-reality gaps until current `master` materializes them again.
- `devres` maps to the bounded shared-helper tranche and should stay split between helper parity and checker-backed packet truthfulness work.
- `landlock/ruleset` maps to the bounded shared-helper tranche and should keep its ownership boundary explicit.
- `landlock/syscalls` maps to the bounded shared-helper tranche and should keep its governance boundary explicit through the shipped `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` helper packet.
- adjacent notifier evidence maps to Phase 13 release-surface truthfulness only and should stay separate from the four helper anchors while keeping the shipped notifier survey, the landed priority-signal guard, the validator-first release handle, the Linux-style make routes, and the shipped `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` direct-evidence shards explicit; direct notifier manifests, the dedicated notifier header, and the remaining list helpers stay repo-reality gaps until current `master` materializes them again

## Libfs Lane Traceability

Keep the current `libfs` mapping explicit through:
- `Documentation/zigux/phase13-libfs-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Current `master` materializes the dedicated `libfs` survey note, the helper-local `fs/libfs.zig` starter, the direct libfs replay, the direct reviewability replay, the manifest-backed helper packet, and the stable validator-first make routes for the `fs/libfs.c` roadmap anchor. If direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, or `zigux/tests/phase13_libfs_addressability.zig` cannot be materialized on current `master`, record them as repo-reality gaps rather than presenting them here as shipped repo evidence.

That bounded `libfs` packet still covers positive-entry classification, simple-directory emptiness planning, negative-dentry lookup shaping, simple transaction acquire, publish, and release planning, plus offset seek, readdir, rename, and rename-exchange planning without claiming live dcache entry insertion, inode lifetime management, page-cache-backed filesystem state, or broader filesystem registration. The dedicated survey note plus the shipped helper-local libfs packet should stay visible here as roadmap-to-repo evidence, and any still-missing slice, shared-build, or addressability companions should stay recorded as repo reality until current `master` materializes them again, but they still support the shared Phase 13 packet rather than creating an extra replay step or a closure claim.

## Landlock Ruleset Lane Traceability

Keep the current `landlock/ruleset` mapping explicit through:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `security/landlock/ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Current `master` materializes the dedicated ownership note, the dedicated survey note, the helper-local `security/landlock/ruleset.zig` starter, the direct replay, the manifest-backed packet, the dedicated packet checker, and the stable validator-first make routes for the `landlock/ruleset` lane. If direct companions such as `Documentation/zigux/phase13-landlock-ruleset-slice.md` or `zigux/tests/phase13_build.zig` cannot be materialized on current `master`, record them as repo-reality gaps rather than presenting them here as shipped repo evidence.

That bounded `landlock/ruleset` packet still covers access-mask accounting, the matching-rule-versus-no-match `insert_rule()` planning split, tree-search outcome planning, and explicit no-match tree-link mode reviewability without claiming live rb-tree mutation, `rb_replace_node()`, object ownership, hierarchy lifetime, deferred frees, or full Landlock enforcement.
The dedicated ownership note, the shipped survey note, the direct replay, the manifest-backed packet, and the shipped helper-local ruleset starter should stay visible here as roadmap-to-repo evidence, and any still-missing slice or shared-build companions should stay recorded as repo reality until current `master` materializes them again, but they still support the shared Phase 13 packet rather than creating an extra replay step or a closure claim.

## Landlock Syscalls Lane Traceability

Keep the current `landlock/syscalls` mapping explicit through:
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Current `master` materializes the dedicated governance note, the dedicated slice note, the dedicated survey note, the helper-local `security/landlock/syscalls.zig` starter, the direct syscall replay, the dedicated reviewability replay, the manifest-backed packet, and the stable validator-first make routes for the `landlock/syscalls` lane. If the older shared `zigux/tests/phase13_build.zig` route cannot be materialized on current `master`, record that direct path as a repo-reality gap rather than presenting it here as shipped repo evidence.

That bounded `landlock/syscalls` packet still covers `landlock_restrict_self()` flag and credential-gate planning, one bounded `landlock_add_rule()` wrapper step for path-beneath and net-port rule validation, explicit ruleset-FD and write-mode validation, and the `ruleset_fops` plus `fop_ruleset_release()` reviewability path without claiming in-memory `get_ruleset_from_fd()` or `get_path_from_fd()` planners, `add_rule_path_beneath()` path handoff, anonymous-fd creation, live FD ownership, path import, credential replacement, thread synchronization, or full Landlock enforcement.
The dedicated governance note, the shipped slice note, the shipped survey note, the shipped helper-local syscalls starter, the direct replay, the dedicated reviewability replay, and the manifest-backed packet should stay visible here as roadmap-to-repo evidence, and the still-missing shared-build companion should stay recorded as repo reality until current `master` materializes it again, but the current helper-local packet already supports the shared Phase 13 tranche rather than creating an extra replay step or a closure claim.

## Broad Surface Expectations

When a shared contributor-facing summary mentions Phase 13, it should keep these expectations visible:
- the packet is still active rather than closed
- the owner split is explicit
- notifier evidence is adjacent support, not a fifth helper slice
- the guidance stays inside helper, docs, checklist, and truthfulness work unless a new roadmap-approved surface lands

## Shared Notes To Keep Aligned

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Checker-Backed Evidence

Keep the roadmap-to-repo map explicit about the shipped or repo-reality-gapped Phase 13 packet-truthfulness checks that sit beside the shared replay:
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py` is still materialized on current `master`; together with `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md` note, the shipped `security/landlock/ruleset.zig` starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, the manifest-backed `zigux/tests/phase13_landlock_ruleset_manifest.json` packet, and the stable make routes, it keeps the roadmap-backed `landlock/ruleset` packet reviewable while `Documentation/zigux/phase13-landlock-ruleset-slice.md` and `zigux/tests/phase13_build.zig` stay framed as repo-reality gaps until current `master` materializes them.
- `security/landlock/syscalls.zig` is the shipped helper-local `landlock/syscalls` starter on current `master`; together with `Documentation/zigux/phase13-landlock-syscalls-governance.md`, the shipped `Documentation/zigux/phase13-landlock-syscalls-slice.md` and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the direct `zigux/tests/phase13_landlock_syscalls.zig` replay, the dedicated `zigux/tests/phase13_landlock_syscalls_reviewability.zig` replay, the manifest-backed `zigux/tests/phase13_landlock_syscalls_manifest.json` packet, and the stable make routes, it keeps the syscall-facing roadmap anchor reviewable as one bounded helper-first packet while the older shared `zigux/tests/phase13_build.zig` route stays framed as a repo-reality gap rather than closure evidence.
- `scripts/zigux/check-phase13-devres-packet-alignment.py` is the shipped direct `devres` truthfulness guard on current `master`; it keeps `zigux/tests/phase13_devres_manifest.json` aligned with `Documentation/zigux/phase13-devres-survey.md` so manifest-backed `devres` release wording cannot drift while the shipped `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_dma_coherent.zig` companions stay explicit, and `zigux/tests/phase13_devres_boundary_evidence.zig` remains a repo-reality gap until current `master` materializes it again.
- If `scripts/zigux/check-phase13-notifier-packet.py` cannot be materialized on current `master`, keep adjacent notifier evidence anchored to `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`, keep the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit, and record the missing checker plus the remaining direct notifier tests-root, dedicated notifier header, and list-helper companions as repo-reality gaps instead of shipped current-master evidence.

## Shared Replay Route

Keep the roadmap traceability note aligned with the stable validator-first Phase 13 replay handles through:
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

If the older shared `zigux/tests/phase13_build.zig` companion cannot be materialized on current `master`, record that one direct path as a repo-reality gap rather than presenting the stable make-route handles as proof that the shared build-backed replay bundle is already back.

Direct evidence outside that stable make-route summary should stay explicit too:
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig` is shipped focused syscall evidence on current `master` and should stay explicit as a direct helper-local validation companion rather than being demoted to a repo-reality gap or inflated into an extra shared replay step.
- adjacent notifier evidence remains release-surface support rather than a fifth helper lane or an extra shared replay step; keep the shipped survey, the landed priority-signal guard, the release validator, the stable make-route handles, and the shipped `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` direct-evidence shards explicit while treating the remaining direct notifier tests-root, dedicated notifier header, and list-helper footholds as repo-reality gaps until current `master` materializes them again.

## Non-Goals

- This note does not reopen Phase 13 into a deeper subsystem-implementation plan.
- This note does not convert notifier evidence into a new helper lane.
- This note does not claim the packet has cleared all future validator or release-surface follow-through.
