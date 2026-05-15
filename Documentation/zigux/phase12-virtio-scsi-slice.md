# Phase 12 virtio_scsi Slice

- `PHASE12_SLICE=virtio-scsi-queue-lab-support`
- reread against live `master` and the current `P12-L09` survey packet on `2026-05-14`
- lane: `P12-L12`
- anchor: `drivers/scsi/virtio_scsi.c`
- refreshed against the current `P12-L13` rollback-and-reversible-delivery survey packet on `2026-05-15` without changing the older support-packet ownership markers that `zigux/tests/phase12_virtio_scsi_packet.zig` and `scripts/zigux/check-phase12-virtio-scsi-packet.py` still enforce

## Shipped packet

- `drivers/scsi/virtio_scsi.zig` is the current complex-driver scaffold on `master`
- `zigux/tests/phase12_virtio_scsi.zig` keeps queue layout, request-queue selection, probe snapshot, host-limit, queue-depth, request-submit sequencing, completion-handback sequencing, command-buffer ownership, io-map, and transport-reset recovery summaries explicit
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` keeps the current export surface reachable
- `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` keeps the second-cycle recovery boundary explicit
- `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` keeps the paired second-cycle rollback boundary explicit so the survey packet can talk about rollback readiness without inventing a broader runtime reset replay
- `zigux/tests/phase12_virtio_scsi_packet.zig` remains the manifest-backed support replay for this bounded infra-prep slice
- `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json` now pins the lane-local metadata cleanup, unresolved support-packet commit state on live `master`, shipped paths, and direct validation commands for the current support packet
- `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` keep the newer `P12-L13` roadmap-gap survey machine-checkable beside the earlier support packet, and that newer survey now makes the rollback owner, smoke-first rollback drill, repeated rollback boundary, request-submit sequencing, completion-handback sequencing, command-buffer ownership, control-path governance, and reversible-delivery recovery summaries explicit without turning this support note into a second survey note
- `zigux/tests/phase12_build.zig` keeps the direct replay, syntax-lab smoke, repeated-replan gate, survey gate, and support packet wired into the shared `phase12` smoke and test routes
- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the support manifest, support replay, slice note, or build route drifts

## Repo-reality gaps

- `drivers/nvme/host/pci.zig` is still absent on the surveyed head
- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head

## Why this packet exists

- The roadmap's complex-driver lane wants infrastructure prep, not another helper family
- `master` already has a real `virtio_scsi` scaffold plus a newer bounded survey packet, so the highest-value same-lane move here is to keep the older support note aligned with that shipped review surface instead of pretending the packet stopped at queue-layout-only evidence
- the roadmap still requires segmented rollout, rollback ownership, and recovery-parity discipline, so the paired support note has to acknowledge the current survey packet's rollback-drill and reversible-delivery wording even while the support checker remains pinned to the older metadata packet
- the older support packet had drifted into stale generic lane metadata and stale commit-pin assumptions, so this note now keeps that risk explicit without reopening driver behavior
- the current survey packet now carries the explicit rollback drill too: keep `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` as the smoke-first reversible-delivery replay bundle instead of leaving that sequence implicit in the build file, Makefile, or fallback catalog alone
- the manifest-backed support replay, the newer survey gate and survey note, and the shared Phase 12 build wiring keep this slice reviewable without claiming broader Phase 12 closure, `scsi_host` registration, or live DMA-backed request flow
- This note intentionally stays scoped to the current `virtio_scsi` support packet and does not claim broader Phase 12 closure
