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
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` as the truthful current-master gap map for the shipped NVMe starter-plus-verifier-plus-direct-test packet plus manifest anchor while the dedicated `nvme_pci` survey, slice, and survey-gate packet remains absent
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- rule: keep this one-commit-pinned-catalog plus one current-master gap-inventory note plus two-anchor split explicit in shared PMO wording; only the `virtio_scsi` catalog is commit-pinned direct replay evidence, and neither the NVMe gap note nor the shared-tree anchors should be promoted into extra commit-pinned fallback artifacts unless dedicated replay files actually land

## Exact Coverage Evidence
- exact coverage evidence checked on `2026-05-13`: the commit-pinned direct replay catalog is currently present on `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` at blob `b85983bd6437e65472f3657d809cd0fb47ab26f2`
- exact coverage evidence checked on `2026-05-13`: the current-master NVMe gap-inventory companion is currently present on `master` as `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` at blob `e7fe1544c7b954a1ee4d4a7e16f103cdb9be4537`, while the bounded shipped foothold it describes is now `drivers/nvme/host/pci.zig` at blob `1f77d01cfca15e93b92d5bc89e3623f2a795290a`, `drivers/nvme/host/pci_verify.zig` at blob `2381ab5fdafb164d076709a4e04bafcc6dabca92`, `zigux/tests/phase12_nvme_pci.zig` at blob `f8afe409d895df5ef257aac03f31d59c49d5e26b`, and `zigux/tests/phase12_nvme_pci_manifest.json` at blob `4cd2f31b16de14f21c64496c9846d1a595642866`
- exact coverage evidence checked on `2026-05-13`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` at blob `11b1f29628705280807ba82be01583dd2023b67e` and `Documentation/zigux/phase12-libbpf-segment-survey.md` at blob `0fcead12c8b5d6dc02898f2ea63f9b9bcf5a5034`
- exact coverage evidence checked on `2026-05-13`: the shared raw-read anchors remain `scripts/zigux/check-build-only-phase12-surface.py` at blob `d1f9169c92a9ff072c46b475d44917ba0115f79b` and `zigux/tests/phase12_build.zig` at blob `9d85b42c5ec84f933954492561cfbbbaed9351be`; the build file now exposes the shipped `smoke` and `test` steps through `smoke_step.dependOn(&run_virtio_net_syntax_tests.step);`, `smoke_step.dependOn(&run_syntax_tests.step);`, `smoke_step.dependOn(&run_repeated_replan_tests.step);`, `smoke_step.dependOn(&run_packet_tests.step);`, `test_step.dependOn(&run_virtio_net_contract_tests.step);`, `test_step.dependOn(&run_virtio_net_syntax_tests.step);`, `test_step.dependOn(&run_contract_tests.step);`, `test_step.dependOn(&run_syntax_tests.step);`, `test_step.dependOn(&run_repeated_replan_tests.step);`, and `test_step.dependOn(&run_packet_tests.step);`
- exact runtime-reality evidence checked on `2026-05-13`: current `master` ships `scripts/zigux/validate-phase12.py` at blob `a1b3895271e811629e92fbb08666ab9812f04a97`, but there is still no shipped `make -C zigux phase12-validate` route and the shared fallback packet remains the existing build-only smoke-first packet rather than a validator-first replay surface

## Review Use
- reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening fallback claims or release wording
- keep the current smoke-first replay order explicit through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- if `zig` is unavailable on `PATH`, reuse that same smoke-first order through the shipped Make routes with `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing `phase12-validate` or another unshipped fallback route
- keep the fallback split honest: the `virtio_scsi` catalog is the only commit-pinned direct replay artifact, the NVMe note is now a current-master gap inventory companion for the shipped starter-plus-verifier-plus-direct-test foothold plus manifest anchor, `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors, and `scripts/zigux/validate-phase12.py` remains unwired support material rather than a shipped validator route
- keep `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` explicit as shared-tree raw-read anchors when GitHub contents reads degrade; they stay part of the shipped smoke-first packet and are not extra commit-pinned fallback artifacts

## Anti-Overlap Notes
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion

## Boundaries
- This note must not imply a shipped `make -C zigux phase12-validate` route, a wired validator-first replay packet, focused-libbpf-only replay, cross-build replay, or promotion of the unwired `scripts/zigux/validate-phase12.py` helper into fallback evidence.
- This note must keep the attached-toolchain override framed as a rerun of the shipped Make routes rather than a separate public fallback artifact or replay surface.
- This note must keep the NVMe map framed as a current-master gap inventory companion for the shipped starter-plus-verifier-plus-direct-test foothold plus manifest anchor rather than as a second commit-pinned direct replay artifact.
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.

## Next Bounded Step
If the fallback split changes later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.
