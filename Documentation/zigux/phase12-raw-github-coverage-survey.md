# Phase 12 Raw GitHub Coverage Survey

This note records the public-read fallback split for the active Phase 12 release packet.

It is a compact fallback overview, not a new replay surface and not a commit-pinned artifact itself.

## Status
- `PHASE12_STATUS=active`
- scope: keep the mixed public fallback story explicit across the shipped Phase 12 driver and libbpf packet without promoting shared-tree anchors into dedicated fallback artifacts
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- libbpf survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`

## Fallback Split
- commit-pinned direct replay catalog:
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the commit-pinned direct fallback catalog for the shipped `virtio_scsi` packet
- driver-local current-master gap inventory companion:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the truthful current-master gap map for the shipped NVMe starter-plus-verifier-plus-direct-test-plus-slice-note-plus-survey-note-plus-survey-gate-plus-manifest packet while the dedicated shared-build route stays absent
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- rule: keep this one-commit-pinned-catalog plus one current-master gap-inventory note plus two-anchor split explicit in shared PMO wording; only the `virtio_scsi` catalog is commit-pinned direct replay evidence, and neither the NVMe gap note nor the shared-tree anchors should be promoted into extra commit-pinned fallback artifacts unless dedicated replay files actually land

## Exact Coverage Evidence
- exact coverage evidence rechecked on `2026-05-16`: the commit-pinned direct replay catalog is currently present on `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` at blob `018afaf83f6598d579878cf0876bdcca9d832771`
- exact coverage evidence rechecked on `2026-05-16`: the current-master NVMe gap-inventory companion is currently present on `master` as `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` at blob `1209c92ff896e731f65f5b281ac41eea8c606a3a`
- exact coverage evidence rechecked on `2026-05-16`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` at blob `21efa77678441e874a21a1df53273b15639e19ae` and `Documentation/zigux/phase12-libbpf-segment-survey.md` at blob `98df4876bf9ba9b5d4747a130e382cd641ca82db`
- exact coverage evidence rechecked on `2026-05-16`: the shared raw-read anchors are currently present on `master` as `python3 scripts/zigux/check-build-only-phase12-surface.py` via checker blob `5ef1b18f3055d90eb7b8728c34effa4b9f7f94a9` and `zigux/tests/phase12_build.zig` at blob `172c4c821d9e55c508ff896439cf497259e5c615`; the build file still exposes the shipped `smoke` and `test` steps for the starter-present `virtio_net` syntax, transmit-recycle, and queue-resume replays plus the shipped `virtio_scsi` syntax, repeated-replan, repeated-rollback, packet, and direct test packet
- exact runtime-reality evidence rechecked on `2026-05-16`: current `master` ships `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `906cf0f47deb96b59063665f4a22b60293ce9210`, `zigux/Makefile` at blob `6641fac96d02f7a96832486109d49b7ccd534bc7`, and `.github/workflows/zigux-bootstrap.yml` at blob `c064e309befa43f25dfb2be7829e971adba91ba8`; the bounded degraded-workflow support route is now shipped as `make -C zigux phase12-validate`, and `scripts/zigux/validate-phase12.py` plus `scripts/zigux/check-phase12-release-readiness-packet.py` now stay inside the shipped `phase12-validate` support bundle while the workflow again runs the same validate, smoke, and full-test commands under the checker-aligned Phase 12 step titles `Validate Phase 12 degraded-workflow bundle`, `Run focused Phase 12 smoke shard`, and `Run Phase 12 complex driver tests`
- exact shared-summary drift rechecked on `2026-05-16`: the earlier reviewer-facing reminder lag and the smaller infrastructure-only workflow-title drift are now both closed on current `master`; `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, and the two shared Phase 12 checker packets now all keep the validator-first support bundle explicit beside the same starter-present `virtio_net` plus smoke-first `virtio_scsi` packet.

## Review Use
- reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `scripts/zigux/README.md` whenever fallback wording changes
- rerun the shared Phase 12 checker packet before widening fallback claims or release wording
- keep the fallback split honest: the `virtio_scsi` catalog is the only commit-pinned direct replay artifact, the NVMe note stays a current-master gap-inventory companion, and the `virtio_net` plus libbpf survey notes remain shared-tree-only anchors rather than extra commit-pinned fallback artifacts
- if `zig` is unavailable on `PATH`, keep using the shipped Make routes in the same order and treat the attached override as a rerun of those existing routes, using `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>` rather than inventing another fallback surface

## Anti-Overlap Notes
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion

## Boundaries
- this note must not treat the shipped validator-first support bundle as a second direct replay packet, a focused-libbpf-only replay, or a cross-build replay
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself

## Next Bounded Step
If the fallback split changes later, update this note together with the shared PMO companions so the Phase 12 packet keeps one truthful public-read story. Current `master` now keeps the fallback split itself aligned, the reviewer-facing reminder packet closed, and the workflow-title alignment restored for the two shared Phase 12 checker packets, so leave this note parked unless a fresh repo-first reread finds a new one-file fallback, support-bundle, or shared-summary drift inside the same shipped release packet.
