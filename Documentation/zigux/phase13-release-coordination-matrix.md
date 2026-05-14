# Phase 13 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status
- `PHASE13_STATUS=active`
- `PHASE13_RELEASE_CLOSED=no`
- shared-summary owner: `PMO / Release Management`
- release companion: `Documentation/zigux/phase13-release-notes-survey.md`
- traceability companion: `Documentation/zigux/phase13-roadmap-traceability.md`
- workflow companion: `Documentation/zigux/phase13-contributor-workflow-guide.md`
- sequencing companion: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- tests-root companion: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- release validator: `scripts/zigux/validate-phase13-release.py`
- shared replay handle: `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`
- shared-summary reread target: `scripts/zigux/README.md`, this matrix, the docs-root Phase 13 companions, and the tests-root companion are the shared surfaces to reread together; current `master` now keeps the docs-root, scripts-root, and tests-root packet aligned around the shipped Landlock packet, the compact PMO coordination companion, and adjacent notifier evidence, so the next same-lane shared-summary follow-up should start from whichever broader Phase 13 reminder drifts next instead of replaying the older scripts-root omission.

## Owner Split
- PMO / Release Management: keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, this matrix, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned around the same active-not-closed Phase 13 packet.
- `libfs` helper packet: keep `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json` explicit as the shipped `libfs` foothold while `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, and `zigux/tests/phase13_libfs_addressability.zig` stay recorded as repo-reality gaps.
- `devres` helper packet: keep `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` explicit while the older `scripts/zigux/check-phase13-devres-packet.py` wording stays marked as stale packet drift. Keep the helper-only DMA/scatterlist boundary explicit here too: the current devres packet still carries no DMA mapping helpers, no live scatterlist ownership, and no `sg_table` lifecycle control.
- `landlock` helper packet: keep `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` aligned as the shipped helper-local Landlock packet.
- adjacent notifier evidence: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, `drivers/tty/hvc/hvc_console.h`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13` explicit as adjacent release-surface support rather than a fifth helper lane.

## Release Handle
1. `python3 scripts/zigux/validate-phase13-release.py`
2. `make -C zigux phase13-validate`
3. `make -C zigux phase13`
4. If direct file reads are degraded, keep the release wording anchored to that same validator-first handle instead of inventing a shared `zigux/tests/phase13_build.zig` replay route, a notifier-only replay route, or a closure-only checklist.

## Repo-Reality Gaps
- `Documentation/zigux/phase13-libfs-slice.md`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_addressability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

Keep those paths framed as repo-reality gaps until current `master` materializes them again.

## Boundaries
- This matrix tracks only the active shared-helper release packet on current `master`.
- This matrix does not close the Phase 13 tranche.
- This matrix does not promote adjacent notifier evidence into a fifth helper anchor.
- This matrix does not imply a broader shared build route than the shipped validator-first make handle.
- This matrix does not widen Phase 13 into runtime HVC parity, deeper security-policy ownership, or unrelated freeze-map status work.

## Review Use
- reread this matrix beside `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever shared Phase 13 wording changes, starting with whether `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` keeps the Phase 13 workflow, shared-helper sequencing, and release-coordination companions explicit beside the same repo-reality wording already used by `scripts/zigux/README.md`, the workflow guide, and the shared-helper sequencing note
- rerun `python3 scripts/zigux/validate-phase13-release.py` before widening PMO release wording
- treat this file as the compact owner-and-gap summary for the current Phase 13 packet, not as a substitute for the helper-local survey notes