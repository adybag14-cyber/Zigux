# Phase 12 Release Closure Checklist

This checklist is the PMO release-closure companion to `Documentation/zigux/phase12-release-sequencing.md`.

It records what must stay true before the active bounded Phase 12 tranche can be described as release-closed.

It is not a closure claim, and it is not itself a shipped replay surface.
## Current status
  * `PHASE12_STATUS=active`
  * `PHASE12_RELEASE_CLOSED=no`
  * sequencing authority: `Documentation/zigux/phase12-release-sequencing.md`
  * compact release-coordination matrix: `Documentation/zigux/phase12-release-coordination-matrix.md`
  * complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  * shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  * shipped build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
  * workflow replay anchor: `.github/workflows/zigux-bootstrap.yml`
  * freeze-map boundary reminder: `Documentation/zigux/freeze-map.md` keeps `net/core/skbuff.c` frozen in C and keeps `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` in boundary-study-only status, so this Phase 12 closure companion must not round queueing, throughput, rollback, or recovery wording up into deep-core delivery claims
  * shared fallback overview note: `Documentation/zigux/phase12-raw-github-coverage-survey.md` keeps the mixed raw-read split explicit and must stay aligned with the two commit-pinned fallback artifacts without being treated as a third commit-pinned fallback artifact
## Shared replay order
  1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  2. `make -C zigux phase12-smoke`
  3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  4. `make -C zigux phase12`
  5. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new Phase 12 entrypoint.
     * `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
     * `make -C zigux phase12 ZIG=<attached-zig-path>`
     * This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.
## Closure checklist
  1. Shared release surfaces still agree.
     * `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` must still describe the same shipped Phase 12 replay packet.
     * Use this checklist as the PMO companion when judging whether those shipped surfaces are ready to be described as release-closed.
     * The shared checker and workflow must stay described as build-only contract enforcement rather than as a broader validator-first release gate.
     * There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, or `make -C zigux phase12-validate` route on `master`.
  2. Replay evidence stays green and explicit.
     * `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
     * `python3 scripts/zigux/check-build-only-phase12-surface.py`
     * `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
     * `make -C zigux phase12-smoke`
     * `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
     * `make -C zigux phase12`
     * When the local runtime needs an attached toolchain override, keep that same order and substitute only `ZIG=<attached-zig-path>` on the shipped Make routes rather than renaming the route into an unshipped validator surface.
  3. The approved four-anchor packet stays reviewable and honest.
     * The active shipped build packet on current `master` is the `virtio_scsi` smoke-first replay: `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` stay wired through `zigux/tests/phase12_build.zig`, while the broader `nvme_pci`, `virtio_net`, and libbpf Phase 12 notes remain planning, survey, fallback, parked, or absent-file companions rather than shipped build outputs on current `master`.
     * The current driver-local doc split must stay explicit too: `nvme_pci` and `virtio_scsi` still ship dedicated slice-and-survey pairs, while `Documentation/zigux/phase12-virtio-net-survey.md` remains the truthful survey-only boundary until live `master` actually lands a separate `Documentation/zigux/phase12-virtio-net-slice.md` surface, and the direct `virtio_net` replay files remain unpublished or absent boundaries rather than shipped smoke-first evidence on current `master`.
     * The bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill must remain described as lab-only reversible-delivery evidence rather than closure-ready runtime recovery.
  4. The public fallback split stays explicit.
     * `Documentation/zigux/phase12-raw-github-coverage-survey.md` should keep the mixed fallback overview explicit as two commit-pinned artifacts plus two shared-tree-only anchors.
     * Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts.
     * `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than implied commit-pinned fallback coverage.
     * During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain shared-tree raw-read anchors for the smoke-first packet rather than extra commit-pinned fallback artifacts.
     * The sequencing note, this checklist, the compact release-coordination matrix, and the shared checker should continue to describe the smoke-first reminder consistently across the shared fallback overview note, the complex-driver anti-overlap companion, the shared libbpf anti-overlap companion, the two commit-pinned fallback notes, and the shared raw-read anchor pair.
  5. Future promotion rules stay honest.
     * If a validator-first or runtime-recovery Phase 12 release route is proposed later, the actual shipped file and replay surface must land on `master` before PMO notes describe it as active release evidence.
     * Until then, release planning should name only the shipped smoke preflight routes, the shared build-and-make replay path, the narrow build-only contract checker, the shared fallback overview note, the shared libbpf anti-overlap companion, and the bounded storage rollback drill.
     * `Documentation/zigux/freeze-map.md` must stay explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study-only targets and are not part of the active Phase 12 complex-driver replay packet or closure evidence.
## Active release blocker
  * Phase 12 is still an active release-planning tranche, not a release-closed packet.
  * The older complex-driver owner-map blocker is now closed on current `master`: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` already keeps `Documentation/zigux/phase12-release-sequencing.md` explicit in both its status companions and its future reread set.
  * The older scripts-root blocker is now closed on current `master`: `scripts/zigux/README.md` now keeps the smoke-first `virtio_scsi` release packet plus the surviving survey-only `virtio_net` boundary and snapshot-backed libbpf survey anchor explicit, while absent direct `phase12_nvme_pci`, `phase12_virtio_net`, and `phase12_libbpf_*` replay families stay parked, survey-only, fallback, or absent boundaries rather than shipped release-packet surfaces.
  * Live GitHub contents readback on 2026-05-12 confirms that this closure companion is now the next narrowest PMO drift instead: current `master` already keeps `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned on the same smoke-first `virtio_scsi` packet, so this checklist should stop presenting the already-landed scripts-root truthfulness repair as unfinished before reopening broader docs-root, checker, fallback, or driver-local wording.
  * Current `master` also already ships the dedicated public-read fallback companions `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, so the older fallback-artifact blocker is closed and should not be treated as the live PMO blocker unless one of those files disappears again.
  * Current `master` still keeps the dedicated libbpf verify shard parked: `Documentation/zigux/phase12-libbpf-verify-shard-note.md` and `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` keep `tools/lib/bpf/zigux_segments/verify.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, and the adjacent reviewability packet explicit as parked or absent-file boundaries inside the active release-facing survey packet, so this closure companion should keep that shard visible without describing it as shipped replay evidence.
  * `Documentation/zigux/README.md` now also keeps `zig build test --build-file zigux/tests/phase12_build.zig --summary all` explicit beside `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`, so the older docs-root replay reminder is no longer the live blocker on `master`.
  * That reread must keep the attached-toolchain override explicit as part of the shipped smoke-first order whenever `zig` is unavailable on `PATH`.
  * Queueing, throughput, rollback, and recovery wording must keep the freeze-map split explicit: this packet can describe bounded driver-local evidence and the lab-only `virtio_scsi` rollback drill, but it must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
  * This checklist should be refreshed whenever the shipped packet changes, but it should stay companion-scoped until the shared replay packet itself satisfies the closure conditions.
  * The next honest same-lane PMO follow-through now shifts to the shared review checklist instead: `Documentation/zigux/review-checklist.md` still overstates the shared Phase 12 packet by naming unpublished direct `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_libbpf_segments.zig`, and `zigux/tests/phase12_libbpf_reviewability.zig` paths as if they were part of the shipped current-`master` review packet, so any later same-lane PMO step should refresh that one file before reopening broader docs-root, checker, fallback, or driver-local wording.
  * Any future PMO follow-through should start by rerunning `scripts/zigux/check-build-only-phase12-surface.py`, then rereading `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-release-sequencing.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then refreshing `Documentation/zigux/review-checklist.md` so it stops presenting unpublished direct `nvme_pci`, absent direct `virtio_net`, and parked libbpf replay files as shipped current-`master` Phase 12 evidence before widening into new wording, extra release claims, or any driver-local or helper-local Phase 12 task.
