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
- stable shared handle: `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` keep the current shared review surface explicit while the older `zigux/Makefile`-backed make routes remain repo-reality gaps
- shared-summary reread target: `zigux/tests/README.md`, this matrix, the workflow guide, the docs-root Phase 13 companions, and the tests-root companion note are the shared surfaces to reread together before widening shared-summary wording

Current `master` keeps the docs-root, tests-root, workflow-guide, and compact PMO coordination packet aligned around the roadmap-owned Phase 13 helper anchors, the directly reread narrow `devres` coordination packet in this run, and explicit gap tracking for broader release surfaces that still need fresh same-lane rereads.

Current `master` keeps that `devres` coordination packet intentionally split across:

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `Documentation/zigux/phase13-devres-survey.md`
- `lib/devres.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`

Current `master` still does not materialize `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, or `Documentation/zigux/phase13-notifier-list-survey.md`, so keep those paths framed as repo-reality gaps rather than as shipped shared Phase 13 release-surface support.

## Owner Split

- PMO / Release Management: keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, this matrix, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned around the same active-not-closed Phase 13 packet while keeping the missing shared-summary, missing notifier-support, and Makefile-backed route surfaces explicit as repo-reality gaps.
- roadmap anchors: keep the shared release wording tied to the four roadmap-owned Linux anchors named in `Documentation/zigux/phase13-roadmap-traceability.md`:
  `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c`
- directly reread helper-local packet in this run: only the current `devres` coordination packet above was re-read file-by-file in this PMO slot, so broad release wording should treat `libfs`, `landlock`, and adjacent notifier support as roadmap-owned companion areas that still require a fresh same-lane reread before this matrix names their current helper packets as directly reverified evidence
- adjacent notifier support: keep notifier evidence adjacent to the shared release surface rather than promoting it into a fifth helper lane, and keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` framed as repo-reality gaps until a fresh reread proves otherwise

## Release Handle

1. `scripts/zigux/README.md`
2. `zigux/tests/README.md`
3. `Documentation/zigux/phase13-contributor-workflow-guide.md`
4. `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
5. `Documentation/zigux/phase13-release-notes-survey.md`

Keep the release wording anchored to that same documentation-and-reminder handle instead of inventing a shared `zigux/Makefile` replay route, a shipped validator-first script path that current `master` does not materialize, or a notifier-only replay route.

## Repo-Reality Gaps

- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `Documentation/zigux/phase13-notifier-list-survey.md`
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
- This matrix does not imply a broader shared build route or Makefile-backed review handle than current `master` can directly support.
- This matrix does not widen Phase 13 into runtime HVC parity, deeper security-policy ownership, or unrelated freeze-map status work.

## Review Use

- reread this matrix beside `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever shared Phase 13 wording changes
- reread `scripts/zigux/README.md`, `zigux/tests/README.md`, and any rematerialized `zigux/Makefile` together before widening PMO release wording
- treat this file as the compact owner-and-gap summary for the current Phase 13 packet, not as a substitute for same-lane helper-local rereads
