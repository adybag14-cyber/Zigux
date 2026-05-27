# Release Planning Index

This note is the top-level PMO index for Zigux release planning on current `master`.

It exists to connect the already-closed tranche records to the still-active release packets without implying broader closure, new replay routes, or deeper subsystem readiness than the current tree actually supports.

## Snapshot Date

- repo-first readback date: `2026-05-27`
- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- commit-train source: `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- lane owner: `pmo-release`

## Current Tranche State

1. Phase 1 is closed and parked through `Documentation/zigux/phase1-closure.md`.
2. Phase 2 is closed and parked through `Documentation/zigux/phase2-closure.md`.
3. Phase 3 is active as a bounded ABI and interop packet through `Documentation/zigux/phase3-abi-slice.md` and its adjacent slice notes. It is not a closed release tranche.
4. Phase 12 is the active complex-driver release packet through `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`. Current `master` keeps this packet active and not closed.
5. Phase 13 is the active shared-helper release packet through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, and `Documentation/zigux/phase13-roadmap-traceability.md`. Current `master` keeps this packet active and not closed.
6. Phase 14 and Phase 15 remain governance and boundary-survey territory. They should not be used as evidence that the active release packets are closed.

## Release Order

Keep PMO release sequencing grounded in the current repo state:

1. Treat Phase 1 and Phase 2 as the only closed tranche prerequisites already recorded in the product docs.
2. Keep Phase 3 framed as a prerequisite substrate packet that stays active and reviewable, but not as a release-closure record.
3. Treat Phase 12 as the current shared release packet for complex-driver coordination.
4. Treat Phase 13 as the current shared release packet for contributor-facing shared-helper coordination.
5. Keep Phase 14 and Phase 15 as downstream governance and study boundaries, not as reasons to widen Phase 12 or Phase 13 release claims.

## Shared Release Packets

### Phase 12

- status: `active`
- closure state: `not closed`
- current shared route family: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`
- bounded shared build packet: the six-file `virtio_net` smoke-and-test set recorded by `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-readiness-survey.md`
- adjacent but non-shared release context: the rollback-lab `virtio_scsi` survey packet, the driver-local NVMe foothold, the parked libbpf reviewability packet, and the raw-GitHub fallback note set

### Phase 13

- status: `active`
- closure state: `not closed`
- stable contributor-facing release handle: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- PMO coordination companions: `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md`
- current repo-reality gap to keep explicit: `zigux/Makefile` is present, but `make -C zigux phase13-validate` and `make -C zigux phase13` are still absent on current `master`

## PMO Boundaries

- Do not promote Phase 3 reminder surfaces into a closure claim.
- Do not treat Phase 12 driver-local survey companions as shared release closure.
- Do not treat Phase 13 adjacent notifier evidence as a fifth roadmap anchor.
- Do not treat Phase 14 or Phase 15 governance notes as proof that active release packets are closed.

## Next Bounded PMO Step

Leave this index parked unless one of these reminder surfaces moves again:

- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`

If one of those surfaces drifts, make the next same-lane follow-through the smallest truthfulness repair in the shared PMO notes before widening into any helper-local, checker-local, or driver-local work.
