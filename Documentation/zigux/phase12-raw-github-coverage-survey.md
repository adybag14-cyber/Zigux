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
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` as the commit-pinned direct fallback catalog for the shipped `virtio_scsi` packet
- driver-local current-master gap inventory companion:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` as the truthful current-master gap map for the shipped NVMe starter-plus-verifier-plus-direct-test-plus-slice-note-plus-survey-note-plus-survey-gate packet plus manifest anchor while the dedicated shared-build route remains absent
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- rule: keep this one-commit-pinned-catalog plus one current-master gap-inventory note plus two-anchor split explicit in shared PMO wording; only the `virtio_scsi` catalog is commit-pinned direct replay evidence, and neither the NVMe gap note nor the shared-tree anchors should be promoted into extra commit-pinned fallback artifacts unless dedicated replay files actually land

## Exact Coverage Evidence
- exact coverage evidence checked on `2026-05-14`: the commit-pinned direct replay catalog is currently present on `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` at blob `049a56ad73afea6187f487b0a27c259439ad00be`
- exact coverage evidence checked on `2026-05-14`: the current-master NVMe gap-inventory companion is currently present on `master` as `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` at blob `bd9e80cb6e6fd9b5fdbaefff85154514d98ff431`, while the bounded shipped foothold it describes is now `drivers/nvme/host/pci.zig` at blob `a0de48386a5c3f2989a405ea5698ab551bfbdbd0`, `drivers/nvme/host/pci_verify.zig` at blob `71de06e8a9c648556679c1c5df726cac4501a277`, `zigux/tests/phase12_nvme_pci.zig` at blob `4751b27d7091f920821f44a854d5fa486a8222c2`, `Documentation/zigux/phase12-nvme-pci-slice.md` at blob `09c03f8c8aa216c678da573c9f900f9dfc2cebaa`, `Documentation/zigux/phase12-nvme-pci-survey.md` at blob `a982577bcc5cf71db8492e39a6fbfff3d6ec88c3`, `zigux/tests/phase12_nvme_pci_survey.zig` at blob `e7a03f4f4f72dfae5ca655bec1b2b054aac68a3d`, and `zigux/tests/phase12_nvme_pci_manifest.json` at blob `723008016b1c4aa25e44f01feb4d67b724254ab4`
- exact coverage evidence checked on `2026-05-14`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` at blob `f4a1fbbdf38e894c253054cd9342d3b23f333516` and `Documentation/zigux/phase12-libbpf-segment-survey.md` at blob `1cbe1532fcaa027eb67f9633f11aef51719eb4b6`
- exact coverage evidence checked on `2026-05-14`: the shared raw-read anchors remain `scripts/zigux/check-build-only-phase12-surface.py` at blob `782eca3b6031b93f96bfe8cdb2da21b9eefc65e5` and `zigux/tests/phase12_build.zig` at blob `d5746e7fc71d926e8e72310f29bca9c9fcdad5fc`; the build file now exposes the shipped `smoke` and `test` steps through `smoke_step.dependOn(&run_virtio_net_syntax_tests.step);`, `smoke_step.dependOn(&run_syntax_tests.step);`, `smoke_step.dependOn(&run_repeated_replan_tests.step);`, `smoke_step.dependOn(&run_repeated_rollback_tests.step);`, `smoke_step.dependOn(&run_packet_tests.step);`, `test_step.dependOn(&run_virtio_net_contract_tests.step);`, `test_step.dependOn(&run_virtio_net_syntax_tests.step);`, `test_step.dependOn(&run_contract_tests.step);`, `test_step.dependOn(&run_syntax_tests.step);`, `test_step.dependOn(&run_repeated_replan_tests.step);`, `test_step.dependOn(&run_repeated_rollback_tests.step);`, and `test_step.dependOn(&run_packet_tests.step);`
- exact runtime-reality evidence checked on `2026-05-14`: current `master` ships `scripts/zigux/validate-phase12.py` at blob `0dc50305690599fd6e6617dce0ba5653c97b86f2`, `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `8d86133321acae6deb1f55063c74c86d4b1387f9`, `zigux/Makefile` at blob `812e7e708b6c6cf3c2879e12e8ce7c906d5d4069`, and `.github/workflows/zigux-bootstrap.yml` at blob `796c2f1c2df51e3cafc2ff7c55e8c3ab345867bd`; the bounded degraded-workflow support route is now shipped as `make -C zigux phase12-validate`, while the shared fallback packet still keeps that validator-first support bundle distinct from the smoke-first direct replay surface rather than treating it as a second direct replay packet.
- exact shared-summary drift checked on `2026-05-15`: the remaining same-family lag has narrowed to the checker-local surface. `Documentation/zigux/review-checklist.md` and `zigux/tests/README.md` now keep the bounded NVMe starter-plus-verifier-plus-direct-test-plus-slice-note-plus-survey-note-plus-survey-gate-plus-manifest packet explicit, while `scripts/zigux/check-build-only-phase12-surface.py` still does not fail-close on that newer tests-root NVMe packet wording; broader docs-root or scripts-root wording remains adjacent shared-summary work rather than part of this note-local fallback split.

## Review Use
- reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening fallback claims or release wording
- keep the current validator-first then smoke-first replay order explicit through `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- if `zig` is unavailable on `PATH`, reuse that same order through the shipped Make routes with `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing another fallback route
- keep the fallback split honest: the `virtio_scsi` catalog is the only commit-pinned direct replay artifact, the NVMe note is now a current-master gap inventory companion for the shipped starter-plus-verifier-plus-direct-test-plus-slice-note-plus-survey-note-plus-survey-gate-plus-manifest packet, `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors, and `scripts/zigux/validate-phase12.py` plus `scripts/zigux/check-phase12-release-readiness-packet.py` now stay inside the shipped `phase12-validate` support bundle rather than acting as standalone direct replay routes
- keep `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` explicit as shared-tree raw-read anchors when GitHub contents reads degrade; they stay part of the shipped smoke-first packet and are not extra commit-pinned fallback artifacts
- keep the narrower shared-summary drift explicit too: `Documentation/zigux/review-checklist.md` and `zigux/tests/README.md` now keep the shipped NVMe starter-plus-verifier-plus-direct-test-plus-slice-note-plus-survey-note-plus-survey-gate-plus-manifest packet explicit, but `scripts/zigux/check-build-only-phase12-surface.py` still does not fail-close on that tests-root wording; reread this note beside the checker before assuming the whole shared reminder packet has caught up, and leave broader docs-root or scripts-root wording to the adjacent shared-summary lane.

## Anti-Overlap Notes
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion

## Boundaries
- This note must not treat the shipped `make -C zigux phase12-validate` route as a second direct replay packet, a focused-libbpf-only replay, a cross-build replay, or a promotion of the `scripts/zigux/validate-phase12.py` helper beyond the shipped validator-first support bundle.
- This note must keep the attached-toolchain override framed as a rerun of the shipped Make routes rather than a separate public fallback artifact or replay surface.
- This note must keep the NVMe map framed as a current-master gap inventory companion for the shipped starter-plus-verifier-plus-direct-test-plus-slice-note-plus-survey-note-plus-survey-gate-plus-manifest packet rather than as a second commit-pinned direct replay artifact.
- This note must keep the shared-summary drift framed as a narrower checker-local reminder lag rather than as proof that the landed NVMe direct packet is missing from current `master`.
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.

## Next Bounded Step
If the fallback split changes later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story. The next same-lane repair should stay checker-local: harden `scripts/zigux/check-build-only-phase12-surface.py` so it fail-closes on the tests-root NVMe packet wording that `Documentation/zigux/review-checklist.md` and `zigux/tests/README.md` now already carry, and leave broader docs-root or scripts-root wording to the adjacent shared-summary lane.
