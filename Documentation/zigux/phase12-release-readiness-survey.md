# Phase 12 Release Readiness Survey

This document records the current release-discipline reading for the active bounded Phase 12 complex-driver tranche without claiming that the roadmap phase is globally closed.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`
- `PHASE12_RELEASE_SURVEY=present`
- `PHASE12_SHARED_VALIDATE_ENTRYPOINT=make -C zigux phase12-validate`
- `PHASE12_SHARED_REPLAY_ENTRYPOINT=make -C zigux phase12`
- scope: roadmap-backed `virtio_net`, `nvme_pci`, `virtio_scsi`, and bounded libbpf helper evidence plus the current cross-compile smoke packet and the mixed public-read fallback coverage packet
- product boundary:
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-readiness-handoff.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase12-shared-replay-contract.md`
  - `Documentation/zigux/phase12-cross-compile-smoke.md`
  - `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `scripts/zigux/check-phase12-cross.py`
  - `scripts/zigux/check-phase12-raw-github-coverage.py`
  - `scripts/zigux/check-phase12-libbpf-focused-replay.py`
  - `scripts/zigux/check-phase12-release-readiness-packet.py`
  - `scripts/zigux/check-phase12-shared-replay-contract.py`
  - `scripts/zigux/validate-phase12.py`
  - `zigux/tests/phase12_cross_build.zig`
  - `zigux/tests/phase12_raw_github_coverage_manifest.json`
  - `zigux/tests/phase12_raw_github_coverage_survey.zig`
  - `zigux/tests/phase12_libbpf_only_build.zig`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`

## Why this record exists

The live repo already carries real Phase 12 survey notes, shared validation wiring, a bounded cross-compile smoke packet, and a mixed raw-GitHub fallback packet. What it did not yet have was one release-facing note that says, in one place, how those pieces should be read together.

This survey closes that PMO gap without widening driver scope:

- the current tranche is active, not closed
- the release-facing note now also names `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test` plus `python3 scripts/zigux/check-phase12-release-readiness-packet.py` as the dedicated PMO packet guard, so this release-coordination note has its own fail-closed review hook instead of relying only on the broader validator and reviewer habit
- the shared validator-first path remains `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- when Devbox or a PATH-provided Zig toolchain is unavailable, the same validator-first route still stays explicit through the attached-toolchain fallback commands `make -C zigux phase12-validate PYTHON=python3 ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of forcing ad hoc release-review reruns
- the non-native compile-smoke packet is an explicit part of the release reading through `Documentation/zigux/phase12-cross-compile-smoke.md`, `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`, and `zigux/tests/phase12_cross_build.zig`
- the public-read fallback posture is intentionally mixed and should stay explicit instead of being inferred from whichever anchor most recently gained a pinned raw catalog
- the release packet should say plainly which anchors have commit-pinned public fallback artifacts today and which still rely on shared-tree fallback reads only
- the release packet now also keeps `Documentation/zigux/phase12-release-coordination-matrix.md` explicit as the compact PMO handoff for the three-way owner split, per-anchor status bucket, shared validation gate, rollback owner, and mixed public-read fallback mode, so that release-facing view does not stay discoverable only from the deeper shared replay contract note
- the release packet now also keeps `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-readiness-handoff.md` explicit as the ordered validate-before-replay route plus the active-not-closed PMO follow-through note, so release sequencing and remaining shared-validator carryover do not stay discoverable only from the matrix or deeper contract notes
- the release packet should also keep the current three-way owner split explicit so `virtio_net`, the shared storage packet around `nvme_pci` and `virtio_scsi`, and `libbpf` do not collapse back into one fuzzy release label during PMO review
- the release packet should keep the shared review checklist visible as part of the same PMO evidence surface so degraded-workflow, build-inventory, raw-fallback, and focused libbpf-only replay questions do not live only in reviewer habit
- the dedicated Phase 12 PMO checklist question now restates the active-not-closed release posture, the approved three-target musl smoke set, and the current two commit-pinned versus two shared-tree-only fallback split in one release-facing prompt instead of leaving that summary only in the survey note and docs root

## Current release reading

The current Phase 12 release-facing reading is:

- `drivers/net/virtio_net.c`: bounded Zig starter plus survey evidence are present through `Documentation/zigux/phase12-virtio-net-survey.md`, but public-read fallback still remains shared-tree-only rather than commit-pinned
- `drivers/nvme/host/pci.c`: bounded Zig starter, survey note, and slice note are present, and the bounded packet also ships `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` for commit-pinned public fallback review
- `drivers/scsi/virtio_scsi.c`: bounded Zig starter, survey note, and slice note are present, and the lane also ships `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` as the current commit-pinned raw fallback catalog with a recorded bounded replay note
- `tools/lib/bpf/libbpf.c`: bounded segmented helper survey evidence is present through `Documentation/zigux/phase12-libbpf-segment-survey.md`, while the release packet now also keeps the focused libbpf-only replay shard explicit through `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `zigux/tests/phase12_libbpf_only_build.zig`, and the dedicated `zig build --build-file zigux/tests/phase12_libbpf_only_build.zig phase12-libbpf-focused-replay --summary all` alias; public-read fallback still remains shared-tree-only rather than map-pinned or catalog-pinned
- `Documentation/zigux/README.md` now also mirrors the mixed fallback split directly, naming `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` as the dedicated commit-pinned fallback artifacts while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only fallback reads
- the same release packet now also keeps the active complex-driver rollback owner split explicit: `Network Driver Lane` owns the bounded `virtio_net` packet, `Storage Driver Lane` owns the bounded `nvme_pci` and `virtio_scsi` packets, and `BPF Tooling Lane` owns the bounded libbpf helper packet
- `Documentation/zigux/phase12-release-coordination-matrix.md` now also keeps that same three-way owner split, the per-anchor status bucket, the shared validation gate, the rollback owner map, and the mixed two commit-pinned versus two shared-tree-only fallback split visible in one compact PMO handoff view
- `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-readiness-handoff.md` now also stay inside the same release packet so PMO review can read the ordered validate-before-replay route and the still-open shared-validator follow-through without treating the matrix as the only coordination surface
- the shared-tree-only side of that fallback split is now also bounded by four published readback roots in `Documentation/zigux/phase12-raw-github-coverage-survey.md`: `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net`, `https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf`, `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`, and `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`, so degraded public review of `virtio_net` and `libbpf` no longer depends on ad hoc tree discovery
- that same mixed fallback packet is also backed by `scripts/zigux/check-phase12-raw-github-coverage.py`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig`, so the release-facing note now names the checker and manifest-backed survey evidence instead of treating the split as prose-only release guidance
- `Documentation/zigux/review-checklist.md` now remains part of the same release-facing packet and carries the shared degraded-workflow, build-inventory, raw-fallback, focused libbpf-only replay, and dedicated Phase 12 PMO release-readiness prompts, so PMO review does not rely on the docs root alone to keep those release checks visible
- `zigux/tests/README.md` now also remains part of the same release-facing packet and keeps the shared degraded-workflow stack, the active-not-closed release posture, the approved three-target musl smoke set, the focused libbpf-only replay shard, the paired raw-coverage manifest plus survey evidence, and the Linux-style validate-before-replay handoff visible from the tests root instead of leaving that PMO route discoverable only through the docs root and scripts root
- the dedicated Phase 12 PMO checklist question now restates the active-not-closed release posture, the approved three-target musl smoke set, and the current two commit-pinned versus two shared-tree-only fallback split in one release-facing prompt instead of leaving that summary only in the survey note and docs root
- `Documentation/zigux/phase12-shared-replay-contract.md` now stays inside the same release packet as the shared-versus-focused replay contract note, keeping the release-readiness packet guard, the raw-GitHub coverage checker, the focused libbpf-only replay shard, and the broader `make -C zigux phase12-validate` before `make -C zigux phase12` handoff explicit in one contributor-facing place instead of leaving that preflight stack split across disconnected notes
- the shared replay packet stays reviewable through `zigux/tests/phase12_build.zig`, `make -C zigux phase12-validate`, and `make -C zigux phase12`
- the compile-smoke packet now stays explicit for the approved non-native musl targets `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` instead of living only as implicit test wiring
- the raw-fallback packet now keeps the split explicit: two anchors have dedicated commit-pinned fallback artifacts, and two anchors still rely on shared-tree fallback reads

- `PHASE12_ROADMAP_ANCHOR_COUNT=4`
- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`
- `PHASE12_APPROVED_CROSS_TARGET_COUNT=3`
- `PHASE12_RELEASE_CLOSED=no`

## Evidence set

The current bounded release-evidence set is:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-handoff.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase12-shared-replay-contract.md`
- `Documentation/zigux/phase12-cross-compile-smoke.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase12-cross.py`
- `scripts/zigux/check-phase12-raw-github-coverage.py`
- `scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `scripts/zigux/check-phase12-libbpf-packet.py`
- `scripts/zigux/check-phase12-libbpf-snapshot.py`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/check-phase12-shared-replay-contract.py`
- `scripts/zigux/validate-phase12.py`
- `zigux/tests/phase12_cross_build.zig`
- `zigux/tests/phase12_build.zig`
- `zigux/tests/phase12_raw_github_coverage_survey.zig`
- `zigux/tests/phase12_raw_github_coverage_manifest.json`
- `zigux/tests/phase12_libbpf_only_build.zig`
- `zigux/tests/phase12_libbpf_segments.zig`
- `zigux/tests/phase12_libbpf_reviewability.zig`
- `zigux/tests/phase12_nvme_pci.zig`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
- `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
- `zigux/tests/phase12_libbpf_manifest.json`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `zigux/Makefile`

## Gates

1. run the raw-GitHub coverage checker
- `python3 scripts/zigux/check-phase12-raw-github-coverage.py --self-test`
- `python3 scripts/zigux/check-phase12-raw-github-coverage.py`

2. run the dedicated release-readiness packet checker
- `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
- `python3 scripts/zigux/check-phase12-release-readiness-packet.py`

3. run the shared replay-contract checker
- `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`
- `python3 scripts/zigux/check-phase12-shared-replay-contract.py`

4. validate the shared Phase 12 survey packet
- `python3 scripts/zigux/validate-phase12.py`

5. run the make-level validation entrypoint
- `make -C zigux phase12-validate`
- attached-toolchain fallback when Devbox or PATH Zig is unavailable: `make -C zigux phase12-validate PYTHON=python3 ZIG=<attached-zig-path>`

6. replay the bounded cross-compile smoke packet
- `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`

7. run the focused libbpf-only replay shard
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `zig build --build-file zigux/tests/phase12_libbpf_only_build.zig phase12-libbpf-focused-replay --summary all`
- `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`

8. run the shared Phase 12 build replay
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

9. run the Linux-style combined Phase 12 entrypoint
- `make -C zigux phase12`
- attached-toolchain fallback when Devbox or PATH Zig is unavailable: `make -C zigux phase12 ZIG=<attached-zig-path>`

## Non-goals

This survey does not claim:

- global Phase 12 closure
- full runtime parity for `virtio_net`, `nvme_pci`, or `virtio_scsi`
- DMA-backed queue ownership, full interrupt or transport lifecycle parity, or deeper probe or teardown flows beyond the current bounded starters
- libbpf object-model, loader, relocation, file-path-and-handle bridge, or perf-buffer-online-cpu-routing closure
- equivalent current-head raw fallback coverage for every Phase 12 anchor

## Next bounded step

If this `pmo-release` lane reopens, the next honest follow-up is to tighten `scripts/zigux/check-phase12-release-readiness-packet.py` so the checker first resyncs with the currently published `P12-L07` raw-fallback packet: its embedded `last_replayed_public_head` expectation and the paired `zigux/tests/phase12_raw_github_coverage_manifest.json` plus `zigux/tests/phase12_raw_github_coverage_survey.zig` markers should match the live `0bd402fd6ca83ba2ace6b21e9e57459401b631cd` packet again before any broader release-packet widening. After that checker-local drift is closed, treat `Documentation/zigux/phase12-release-coordination-matrix.md` as a first-class release-packet summary surface and keep the paired `zigux/tests/README.md` PMO handoff sentence fail-closed too. Keep that work bounded to the dedicated release-packet checker plus adjacent PMO guidance wording without reopening DMA transport, queue ownership, throughput, recovery, object-model, loader, relocation, helper behavior, or direct driver behavior.
