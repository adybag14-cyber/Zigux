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
- dedicated public fallback artifacts:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` as the repo-reality gap map for the absent direct `nvme_pci` packet on current `master`
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` as the commit-pinned direct fallback catalog for the shipped `virtio_scsi` packet
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- rule: keep this two-artifact-plus-two-anchor split explicit in shared PMO wording; only the `virtio_scsi` artifact is a commit-pinned direct replay catalog, and the shared-tree anchors must not be promoted into dedicated fallback artifacts unless those files actually land

## Exact Coverage Evidence
- exact coverage evidence checked on `2026-05-12`: the dedicated fallback artifacts are currently present on `master` as `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` at blob `4ce9b0d2ea78fe62f11b2d33e5ae151571e543fb` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` at blob `4ed48ba555e2507eda195d5d5c3450e0cee85840`
- exact coverage evidence checked on `2026-05-12`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` at blob `4085de5a49b8ff7a57d7d81aefb5a1d54a5e7704` and `Documentation/zigux/phase12-libbpf-segment-survey.md` at blob `3da97816df567e85309a38948ceb158d2b47efae`
- exact coverage evidence checked on `2026-05-12`: the shared raw-read anchors remain `scripts/zigux/check-build-only-phase12-surface.py` at blob `12cbff19b9084407a708ac080f4805d0decddebd` and `zigux/tests/phase12_build.zig` at blob `9d85b42c5ec84f933954492561cfbbbaed9351be`; the build file now exposes the shipped `smoke` and `test` steps through `smoke_step.dependOn(&run_virtio_net_syntax_tests.step);`, `smoke_step.dependOn(&run_syntax_tests.step);`, `smoke_step.dependOn(&run_repeated_replan_tests.step);`, `smoke_step.dependOn(&run_packet_tests.step);`, `test_step.dependOn(&run_virtio_net_contract_tests.step);`, `test_step.dependOn(&run_virtio_net_syntax_tests.step);`, `test_step.dependOn(&run_contract_tests.step);`, `test_step.dependOn(&run_syntax_tests.step);`, `test_step.dependOn(&run_repeated_replan_tests.step);`, and `test_step.dependOn(&run_packet_tests.step);`
- exact runtime-reality evidence checked on `2026-05-12`: current `master` ships `scripts/zigux/validate-phase12.py` at blob `11ecca64bbaeacc62e08e0563c224c2b0a4e1e55`, but there is still no shipped `make -C zigux phase12-validate` route and the shared fallback packet remains the existing build-only smoke-first packet rather than a validator-first replay surface

## Review Use
- reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening fallback claims or release wording
- keep the current smoke-first replay order explicit through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- if `zig` is unavailable on `PATH`, reuse that same smoke-first order through the shipped Make routes with `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing `phase12-validate` or another unshipped fallback route
- keep `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` explicit as shared-tree raw-read anchors when GitHub contents reads degrade; they stay part of the shipped smoke-first packet and are not extra commit-pinned fallback artifacts

## Anti-Overlap Notes
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion

## Boundaries
- This note must not imply a shipped `make -C zigux phase12-validate` route, a wired validator-first replay packet, focused-libbpf-only replay, cross-build replay, or promotion of the unwired `scripts/zigux/validate-phase12.py` helper into fallback evidence.
- This note must keep the attached-toolchain override framed as a rerun of the shipped Make routes rather than a separate public fallback artifact or replay surface.
- This note must keep the `nvme_pci` companion framed as the current repo-reality gap map rather than a claim that the direct `nvme_pci` packet is still shipped on `master`.
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.

## Next Bounded Step
If the fallback split changes later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.
