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

If direct notifier companions such as `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, or `drivers/tty/hvc/hvc_console.h` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped evidence.

## Traceability Map

- `libfs` maps to the bounded shared-helper tranche and should stay represented as its own contributor-facing bucket.
- `devres` maps to the bounded shared-helper tranche and should stay split between helper parity and checker-backed packet truthfulness work.
- `landlock/ruleset` maps to the bounded shared-helper tranche and should keep its ownership boundary explicit.
- `landlock/syscalls` maps to the bounded shared-helper tranche and should keep its governance boundary explicit.
- adjacent notifier evidence maps to Phase 13 release-surface truthfulness only and should stay separate from the four helper anchors while keeping the shipped notifier survey, the landed priority-signal guard, the validator-first release handle, and the Linux-style make routes explicit; direct notifier ABI, helper, tests-root, and header footholds stay repo-reality gaps until current `master` materializes them again

## Landlock Ruleset Lane Traceability

Keep the current `landlock/ruleset` mapping explicit through:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`

If direct companions such as `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_ruleset.zig`, or `zigux/tests/phase13_build.zig` cannot be materialized on current `master`, record them as repo-reality gaps rather than presenting them here as shipped repo evidence.

That bounded `landlock/ruleset` packet still covers access-mask accounting, the matching-rule-versus-no-match `insert_rule()` planning split, tree-search outcome planning, and explicit no-match tree-link mode reviewability without claiming live rb-tree mutation, `rb_replace_node()`, object ownership, hierarchy lifetime, deferred frees, or full Landlock enforcement.
The dedicated ownership note should stay visible here as roadmap-to-repo evidence, and any still-missing slice, survey, manifest, or direct test companions should stay recorded as repo reality until current `master` materializes them again, but they still support the shared Phase 13 packet rather than creating an extra replay step or a closure claim.

## Landlock Syscalls Lane Traceability

Keep the current `landlock/syscalls` mapping explicit through:
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Current `master` still keeps the dedicated governance note and the shared release handles explicit for the `landlock/syscalls` lane, but the direct tests-root companions `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` remain repo-reality gaps until current `master` materializes them again.

That bounded `landlock/syscalls` packet still covers `landlock_restrict_self()` flag and credential-gate planning, one bounded `landlock_add_rule()` wrapper step for path-beneath and net-port rule validation, explicit ruleset-FD and write-mode validation, and the `ruleset_fops` plus `fop_ruleset_release()` reviewability path without claiming in-memory `get_ruleset_from_fd()` or `get_path_from_fd()` planners, `add_rule_path_beneath()` path handoff, anonymous-fd creation, live FD ownership, path import, credential replacement, thread synchronization, or full Landlock enforcement.
The dedicated governance note should stay visible here as roadmap-to-repo evidence, and any still-missing direct-test or reviewability companions should stay recorded as repo reality until current `master` materializes them again, but they still support the shared Phase 13 packet rather than creating an extra replay step or a closure claim.

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
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Checker-Backed Evidence

Keep the roadmap-to-repo map explicit about the shipped or repo-reality-gapped Phase 13 packet-truthfulness checks that sit beside the shared replay:
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py` is still materialized on current `master` and keeps `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `Documentation/zigux/phase13-landlock-ruleset-ownership.md` aligned as one roadmap-backed `landlock/ruleset` packet while the direct tests-root companions remain subject to repo reality.
- `scripts/zigux/check-phase13-devres-packet-alignment.py` is the shipped direct `devres` truthfulness guard on current `master`; it keeps `Documentation/zigux/phase13-devres-survey.md` aligned with the live manifest-backed `devres` packet while `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_boundary_evidence.zig` remain repo-reality gaps.
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, and `Documentation/zigux/phase13-release-notes-survey.md` keep the syscall-facing roadmap anchor explicit on current `master`, while `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` remain repo-reality gaps until the direct tests-root companions materialize again.
- If `scripts/zigux/check-phase13-notifier-packet.py` cannot be materialized on current `master`, keep adjacent notifier evidence anchored to `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`, and record the missing checker plus direct notifier ABI, helper, tests-root, and HVC header companions as repo-reality gaps instead of shipped current-master evidence.

## Shared Replay Route

Keep the roadmap traceability note aligned with the stable validator-first Phase 13 replay handles through:
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

If direct companions such as `scripts/zigux/validate-phase13-release.py`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, or `zigux/tests/phase13_libfs_reviewability.zig` cannot be materialized on current `master`, record those direct paths as repo-reality gaps rather than presenting them here as shipped build-backed evidence.

Direct evidence outside that stable make-route summary should stay explicit too:
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig` remains focused syscall evidence only when current `master` can materialize it; otherwise record it as a repo-reality gap instead of an extra shipped replay step.
- adjacent notifier evidence remains release-surface support rather than a fifth helper lane or an extra shared replay step; keep the shipped survey, the landed priority-signal guard, the release validator, and the stable make-route handles explicit while treating direct notifier ABI, helper, tests-root, and header footholds as repo-reality gaps until current `master` materializes them again.

## Non-Goals

- This note does not reopen Phase 13 into a deeper subsystem-implementation plan.
- This note does not convert notifier evidence into a new helper lane.
- This note does not claim the packet has cleared all future validator or release-surface follow-through.
