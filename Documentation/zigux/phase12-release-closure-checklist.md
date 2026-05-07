# Phase 12 Release Closure Checklist

This checklist is the PMO release-closure companion to `Documentation/zigux/phase12-release-sequencing.md`.

It records what must stay true before the active bounded Phase 12 tranche can be described as release-closed.

It is not a closure claim, and it is not itself a shipped replay surface.

## Current status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- sequencing authority: `Documentation/zigux/phase12-release-sequencing.md`
- compact release-coordination matrix: `Documentation/zigux/phase12-release-coordination-matrix.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shipped build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- workflow replay anchor: `.github/workflows/zigux-bootstrap.yml`
- freeze-map boundary reminder: `Documentation/zigux/freeze-map.md` keeps `net/core/skbuff.c` frozen in C and keeps `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` in boundary-study-only status, so this Phase 12 closure companion must not round queueing, throughput, rollback, or recovery wording up into deep-core delivery claims
- shared fallback overview note: `Documentation/zigux/phase12-raw-github-coverage-survey.md` keeps the mixed raw-read split explicit and must stay aligned with the two commit-pinned fallback artifacts without being treated as a third commit-pinned fallback artifact

## Shared replay order
1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new Phase 12 entrypoint.
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`
   - This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.

## Closure checklist
1. Shared release surfaces still agree.
   - `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` must still describe the same shipped Phase 12 replay packet.
   - Use this checklist as the PMO companion when judging whether those shipped surfaces are ready to be described as release-closed.
   - The shared checker and workflow must stay described as build-only contract enforcement rather than as a broader validator-first release gate.
   - There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, or `make -C zigux phase12-validate` route on `master`.
2. Replay evidence stays green and explicit.
   - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
   - `python3 scripts/zigux/check-build-only-phase12-surface.py`
   - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-smoke`
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12`
   - When the local runtime needs an attached toolchain override, keep that same order and substitute only `ZIG=<attached-zig-path>` on the shipped Make routes rather than renaming the route into an unshipped validator surface.
3. The approved four-anchor packet stays reviewable and honest.
   - The active tranche remains the shipped `nvme_pci`, `virtio_net`, `virtio_scsi`, and libbpf survey-backed packet described by the committed Phase 12 manifests under `zigux/tests/`, the committed Phase 12 survey-backed test modules under `zigux/tests/`, the focused direct smoke modules `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, and `tools/lib/bpf/zigux_segments/manifest.json`.
   - The current driver-local doc split must stay explicit too: `nvme_pci` and `virtio_scsi` still ship dedicated slice-and-survey pairs, while `Documentation/zigux/phase12-virtio-net-survey.md` remains the truthful survey-only boundary until live `master` actually lands a separate `Documentation/zigux/phase12-virtio-net-slice.md` surface, even though the smoke-first replay already includes the direct `zigux/tests/phase12_virtio_net_syntax_lab.zig` shard.
   - The bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill must remain described as lab-only reversible-delivery evidence rather than closure-ready runtime recovery.
4. The public fallback split stays explicit.
   - `Documentation/zigux/phase12-raw-github-coverage-survey.md` should keep the mixed fallback overview explicit as two commit-pinned artifacts plus two shared-tree-only anchors.
   - Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts.
   - `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than implied commit-pinned fallback coverage.
   - The sequencing note, this checklist, and the shared checker should continue to describe the smoke-first reminder consistently across the shared fallback overview note and the two commit-pinned fallback notes.
5. Future promotion rules stay honest.
   - If a validator-first or runtime-recovery Phase 12 release route is proposed later, the actual shipped file and replay surface must land on `master` before PMO notes describe it as active release evidence.
   - Until then, release planning should name only the shipped smoke preflight routes, the shared build-and-make replay path, the narrow build-only contract checker, the shared fallback overview note, and the bounded storage rollback drill.
   - `Documentation/zigux/freeze-map.md` must stay explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study-only targets and are not part of the active Phase 12 complex-driver replay packet or closure evidence.

## Active release blocker
- Phase 12 is still an active release-planning tranche, not a release-closed packet.
- The remaining PMO job is drift control across the shipped docs-root, review checklist, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, the `nvme_pci` slice-and-survey pair plus `zigux/tests/phase12_nvme_pci.zig` and `drivers/nvme/host/pci_verify.zig`, the `virtio_net` survey-only boundary plus `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_net_syntax_lab.zig`, the `virtio_scsi` slice-and-survey pair plus `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, the libbpf survey plus `zigux/tests/phase12_libbpf_segments.zig` and `zigux/tests/phase12_libbpf_reviewability.zig`, scripts-root, tests-root, workflow, Makefile, sequencing, this closure-checklist companion, and the two commit-pinned fallback-note surfaces so they keep naming the same bounded release route.
- `zigux/tests/README.md` now keeps `Documentation/zigux/phase12-release-closure-checklist.md` visible from the shared Phase 12 tests-root packet, so the earlier tests-root reminder gap is no longer the live blocker on `master`.
- `scripts/zigux/check-build-only-phase12-surface.py` now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set, so the closure companion is enforced by the shipped checker instead of remaining only a docs-root, sequencing-note, and tests-root reminder.
- The shared fallback overview note must stay in that same reread packet too, because it records the two-artifact-plus-two-anchor split that the narrower driver-local fallback notes do not describe together in one place.
- The PMO companion now also keeps the attached-toolchain fallback explicit for runtimes that do not expose `zig` on `PATH`, and `scripts/zigux/check-build-only-phase12-surface.py` now fails closed on that smoke-first override wording so shared-surface rereads treat it as part of the shipped Phase 12 packet rather than companion-only guidance.
- The smallest same-lane follow-through is now shared-surface drift control rather than another checker-local closure-companion update.
- Queueing, throughput, and recovery language must keep the freeze-map split explicit: this release packet can describe bounded driver-local, libbpf, and lab-only rollback evidence, but it must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- This checklist should be refreshed whenever the shipped packet changes, but it should stay companion-scoped until the shared replay packet itself satisfies the closure conditions.
- Any future PMO follow-through should therefore start by rerunning `scripts/zigux/check-build-only-phase12-surface.py`, then rereading `zigux/tests/README.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, and the other shipped Phase 12 packet surfaces before widening into new wording, extra release claims, or any driver-local or helper-local Phase 12 task.
