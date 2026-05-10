# Phase 12 Complex Driver Lane Sequencing

This note records the bounded owner map for the active Phase 12 complex-driver lanes only.

It is an anti-overlap companion for the current tranche, not a release-order note, a libbpf packet, or a closure claim.

## Current posture
- `PHASE12_STATUS=active`
- complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`
- excluded from this note on purpose: the shared PMO release packet and the non-driver libbpf helper packet
- shared replay routes that all three driver lanes may mention but do not own: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- when `zig` is unavailable on `PATH`, those same shared replay routes may be rerun as `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>`; this note treats that as an environment override for the same shared packet rather than as driver-local ownership or a separate `phase12-validate` route
- shared coordination surfaces that stay non-owner here: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`
- freeze-boundary guard that also stays non-owner here: `Documentation/zigux/freeze-map.md`; queueing, throughput, rollback, and recovery wording inside these three driver lanes must stay below active delivery claims against frozen `net/core/skbuff.c` and below boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c`

## Why this note exists

The Phase 12 roadmap names three high-risk driver anchors under one tranche: `drivers/net/virtio_net.c`, `drivers/nvme/host/pci.c`, and `drivers/scsi/virtio_scsi.c`.

Current `master` already keeps those lanes reviewable through one shared smoke-plus-build packet, but the live driver evidence is deliberately uneven:
- `virtio_net` is still survey-backed and shared-tree-only, with no separate slice note or commit-pinned fallback artifact on `master`
- `nvme_pci` has a dedicated slice note, survey note, commit-pinned raw GitHub fallback map, and a direct smoke verify shard
- `virtio_scsi` has a dedicated slice note, survey note, commit-pinned raw GitHub fallback catalog, and the current lab-only rollback drill

That asymmetry is honest, but it makes overlap easy unless the lane boundaries stay explicit.

## Driver lane map
- `virtio_net` lane:
  Owns `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, and `drivers/net/virtio_net.zig`.
  The bounded live scope is the probe snapshot starter plus the directly coupled syntax-lab, queue-recovery, receive-refill, control-queue-restore, transmit-recycle, mergeable-buffer-length, and repeated-recovery-cycle follow-ups, plus the landed segmented-rollout boundary that keeps the lane below live DMA-backed runtime data-path work.
  It must stay below live DMA-backed runtime data-path work and must remain a shared-tree-only anchor unless a real commit-pinned fallback artifact lands.
- `nvme_pci` lane:
  Owns `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `drivers/nvme/host/pci.zig`, and `drivers/nvme/host/pci_verify.zig`.
  The bounded live scope is the landed queue-count reservation, queue-reservation replay, PRP buffer-shape, PRP metadata, recovery replay, bounded dropped-I/O backlog retirement, and the direct verify shard that keeps that starter explicit inside the shared smoke packet.
  It stays parked unless the roadmap explicitly approves a transport-facing follow-up beyond that current storage-driver starter.
- `virtio_scsi` lane:
  Owns `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `drivers/scsi/virtio_scsi.zig`.
  The bounded live scope is the landed queue-layout, probe-config snapshot, direct syntax-lab shard, and recovery packet, plus the lab-only rollback drill recorded in `Documentation/zigux/phase12-virtio-scsi-slice.md`.
  That rollback drill is storage-lane-local evidence, not a shared Phase 12 recovery claim.

## Shared non-owner surfaces
- `Documentation/zigux/phase12-release-sequencing.md` owns the release-order story for the tranche, not the next driver-local implementation step.
- `Documentation/zigux/phase12-release-closure-checklist.md` is the PMO closure companion, not a driver-lane planner.
- `Documentation/zigux/phase12-release-readiness-survey.md` is the adjacent PMO readiness note, not a driver-lane planner or ownership transfer surface.
- `Documentation/zigux/phase12-raw-github-coverage-survey.md` owns the mixed fallback-overview split for the active tranche, so driver lanes should reread it beside this note instead of treating it as a driver-local fallback artifact.
- `Documentation/zigux/phase12-release-coordination-matrix.md` keeps the compact lane-owner split, fallback split, and smoke-set summary explicit for PMO drift control, so driver lanes should reread it beside this note instead of leaving that compact release view implied from broader PMO prose.
- `Documentation/zigux/freeze-map.md` keeps the deep-core non-goals explicit for this tranche, so driver lanes should reread it beside this note instead of letting driver-local queueing, throughput, rollback, or recovery wording drift into `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c` delivery claims.
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` keeps the shared libbpf reviewability lane, helper-sized ready-next follow-through, deferred bridge and queue-routing work, and the blocked object-model wall separate from the driver lanes, so complex-driver work should reread it beside this note instead of leaving the non-driver libbpf packet as unnamed shared context.
- Driver-local survey notes that rely on this owner map should name `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` explicitly instead of referring to an unnamed lane note, so the anti-overlap anchor stays discoverable from the active `virtio_net`, `nvme_pci`, and `virtio_scsi` packet.
- `scripts/zigux/check-build-only-phase12-surface.py` and `.github/workflows/zigux-bootstrap.yml` enforce the shared build-only review surface, not driver-local ownership.
- `Documentation/zigux/phase12-libbpf-segment-survey.md` and `tools/lib/bpf/zigux_segments/manifest.json` remain real Phase 12 evidence, but they belong to the non-driver helper packet and should not be absorbed into this driver-only map.

## Anti-overlap rules
- Do not let the `virtio_net` lane inherit the storage-lane fallback artifacts or the `virtio_scsi` rollback drill just because all three drivers share `phase12_build.zig`.
- Do not let the `nvme_pci` lane reuse `virtio_scsi` rollback wording as storage-wide recovery proof; its live packet is still the smaller queue-count reservation, queue-reservation replay, PRP-shape, PRP-metadata, recovery replay, bounded backlog-retirement, and direct verify starter.
- Do not let the shared smoke packet turn `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, or `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` into tranche-wide evidence; those focused smoke shards remain lane-local proofs for `nvme_pci`, `virtio_net`, and `virtio_scsi` respectively.
- Do not let shared review surfaces collapse the active tranche to smoke-only shorthand; `zig build test --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12` remain part of the shipped shared replay order even while `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` stay lane-local smoke proofs.
- Do not let lane-local queueing, throughput, rollback, or recovery wording round itself up into active delivery claims against frozen `net/core/skbuff.c` or boundary-study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`; those anchors remain outside the active Phase 12 driver packet unless the freeze map changes first.
- Do not let the `virtio_scsi` lane recast the `virtio_net` syntax-lab shard or the `nvme_pci` PRP helpers as shared storage evidence.
- Do not treat the shared smoke, build, Makefile, workflow, README, PMO notes, compact release-coordination matrix, the shared libbpf anti-overlap companion, or the shared raw-coverage overview as ownership transfer. Those surfaces coordinate the three driver lanes; they do not merge them.

## Next bounded step

Leave this note parked unless fresh repo inspection shows that the shared Phase 12 docs, review-checklist, scripts-root summary, tests-root summary, fallback-overview, compact release-coordination matrix, or shared libbpf anti-overlap surfaces are blurring `virtio_net`, `nvme_pci`, and `virtio_scsi` back together.

The older saved checker self-test follow-through is now stale on `master`: `scripts/zigux/check-build-only-phase12-surface.py` already carries the stronger generic marker-removal self-test loop, so replaying the one-branch docs-root closure-marker handoff would have been churn.

The saved docs-root release-readiness checker follow-through is now also closed on `master`: `scripts/zigux/check-build-only-phase12-surface.py` already requires `Documentation/zigux/phase12-release-readiness-survey.md` inside the docs-root Phase 12 note list, so this lane no longer needs to steer future runs back through that same one-line checker guard.

The older docs-root smoke-summary gap is also closed on `master`: `Documentation/zigux/README.md` now explicitly names `drivers/nvme/host/pci_verify.zig`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all` beside the shared Phase 12 packet, so this lane no longer needs to steer future runs back through that same broad docs-root reminder.

The older shared tests-root release-readiness reminder is now also closed on `master`: `zigux/tests/README.md` now keeps the canonical deterministic replay path at `zigux/tests/phase12_libbpf_snapshot_determinism.zig` beside `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, matching the docs-root packet, the build-only checker, and this lane note.
That closes the prior tests-root-only exception, so this lane no longer needs to steer future runs back through that same one-file determinism-path repair.

The later docs-root fallback-catalog undercount is now also closed on `master`: `Documentation/zigux/README.md` now explicitly names `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` beside the shared Phase 12 packet, so this lane no longer needs to steer future runs back through that PMO-owned docs-root reminder either.

The later raw-fallback shared-surface follow-through is now also closed on `master`: `Documentation/zigux/phase12-raw-github-coverage-survey.md` now explicitly keeps `Documentation/zigux/phase12-release-closure-checklist.md` in its aligned release-facing surface list and separately reminds readers to keep `Documentation/zigux/freeze-map.md` visible when queueing, throughput, rollback, or recovery wording shifts, so this lane no longer needs to steer future runs back through that fallback-overview sync.

The later scripts-root shared replay undercount is now also closed on `master`: `scripts/zigux/README.md` explicitly keeps `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` visible beside the same Phase 12 shared packet, matching `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `zigux/tests/README.md`, and `scripts/zigux/check-build-only-phase12-surface.py`.
That closes the older scripts-root-only reminder, so this lane no longer needs to steer future runs back through that same shared replay-route sync.

If this lane reopens, start by rereading `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` against this note before reopening only the next smallest same-lane shared-surface drift that still blurs the three driver lanes together.

The adjacent PMO release note, `Documentation/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, and `zigux/tests/README.md` now all pin `zigux/tests/phase12_libbpf_snapshot_determinism.zig` as the canonical deterministic replay path and keep only `zigux/tests/fixtures/phase12_libbpf_snapshot.json` plus `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` under the fixtures tree. The scripts-root summary now keeps the shared replay-route markers explicit too, so the older deterministic-path reminder itself is fully closed on `master`.
If this lane needs another bounded step later, re-run the same shared-surface diff first and only reopen the next smallest note, checklist, README, matrix, or checker drift that still survives that reread.

The earlier shared checklist undercount is now closed on `master`: `Documentation/zigux/review-checklist.md` already keeps the adjacent release-readiness note explicit beside the PMO closure companion, the two commit-pinned fallback artifacts, the compact release-coordination matrix, the two anti-overlap companions, and the freeze-boundary reminder.

The later shared checklist drift is now also closed on `master`: `Documentation/zigux/review-checklist.md` now keeps `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, and `zigux/tests/phase12_libbpf_snapshot_determinism.zig` explicit beside the rest of the shared Phase 12 packet, matching the docs-root, scripts-root, tests-root, build-only checker, and libbpf anti-overlap surfaces that already named that deterministic libbpf evidence.

The next still-open same-lane drift is narrower and tests-root only: `Documentation/zigux/phase12-release-readiness-survey.md` now tells future rereads to confirm that `zigux/tests/README.md` keeps `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` explicit beside the same shared Phase 12 packet, but the live tests-root summary still names `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` without the matching `virtio_scsi` fallback catalog.
Future same-lane work should close that one-file tests-root undercount before reopening PMO-owned release wording or the shared libbpf anti-overlap packet.

That follow-through clears the last saved checklist-local reminder in this note. If this lane needs a new bounded step later, re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, and `Documentation/zigux/phase12-raw-github-coverage-survey.md` together first, then only reopen the smallest same-lane shared-surface drift instead of steering back into an already-landed checklist repair.
