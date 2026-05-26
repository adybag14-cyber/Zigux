# Phase 12 Release Closure Checklist

This checklist is the tranche-closure companion for the active Phase 12 packet.

It is a PMO release artifact only. It does not claim that Phase 12 is already closed, and it does not create a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- shared sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`
- shared readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- shared coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`
- validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`
- shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`

## Closure Gates

Keep Phase 12 marked open until every item below is true on current `master`:

- The shared PMO packet stays aligned across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this checklist, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.
- The directly readable validator-first support bundle still reruns as `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`, and `python3 scripts/zigux/validate-phase12.py`; keep `make -C zigux phase12-validate` explicit here as shipped wrapper evidence again on current `master`.
- The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence.
- The shared smoke-first replay packet still stays wired through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`; treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped wrapper evidence again.
- The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`.
- The broader starter-present `virtio_net` direct and syntax-lab packet, the survey-backed `virtio_scsi` rollback-evidence-only packet, and the bounded driver-local `nvme_pci` foothold stay explicit as adjacent review surfaces outside the shared `smoke` and `test` build route.
- The current driver-local `virtio_scsi` split must stay explicit too: current `master` keeps the dedicated `Documentation/zigux/phase12-virtio-scsi-slice.md` plus `Documentation/zigux/phase12-virtio-scsi-survey.md` pair together with `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig`, while `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` remain absent on current `master`.
- The Phase 12 closure packet stays limited to build-only helper evidence, deterministic libbpf snapshot fixtures, segmented release coordination, and the bounded storage rollback drill rather than runtime queue, DMA, recovery, or throughput claims.
- The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required before the shared release packet can be described as ready for closure review.
- The bounded driver-local `nvme_pci` foothold stays explicit as a published-but-still-unwired packet outside the shared smoke-first route rather than being silently promoted into the shared replay set.
- The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.
- The fallback split stays truthful: one commit-pinned `virtio_scsi` replay catalog, one current-master `nvme_pci` gap-inventory companion, and two shared-tree anchors.
- `Documentation/zigux/phase12-raw-github-coverage-survey.md` should keep the mixed fallback overview explicit as one commit-pinned direct replay catalog plus one current-master gap-inventory companion plus two shared-tree-only anchors.
- Phase 12 wording still stays below DMA-safe receive ownership, refill execution, live queue restart parity, transport-backed queue flow, NAPI, XDP, XSK, RSS programming, control-virtqueue runtime traffic, and full `net_device` lifecycle claims.
- `Documentation/zigux/freeze-map.md` still remains the boundary owner for deeper `skbuff`, `workqueue`, and `ring_buffer` anchors.

## Current Open Blockers

Keep the checklist in the open state while these Phase 12 closure blockers remain true:

- `virtio_net` is starter-present and reviewable, but it is still not a release-closed complex-driver packet.
- `virtio_scsi` remains a survey-backed rollback-evidence-only packet outside the shared `phase12` smoke-and-test route; the dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` rerun stays part of that rollback-only evidence while the driver-local starter, direct replay, syntax lab, repeated replan gate, and repeated rollback gate remain absent on current `master`, so it is not yet a deeper runtime-delivery or transport-complete packet.
- `nvme_pci` remains driver-local and outside the shared `phase12` smoke-and-test route.
- The libbpf Phase 12 packet remains parked behind survey, snapshot, and verify-shard reminder surfaces rather than a shipped direct replay bundle.
- The directly readable validator-first support bundle still lives in `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and current `zigux/Makefile` now ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`; those returned wrappers still do not close the broader complex-driver tranche by themselves.
- The shared support packet still has mixed evidence roles on current `master`: the contents bridge now directly reads the scripts-side support bundle, workflow, scripts-root README, current Makefile, and `zigux/tests/phase12_build.zig`, but `Documentation/zigux/phase12-raw-github-coverage-survey.md` still keeps that set framed as bounded reminder evidence rather than broad shared-packet proof while the returned NVMe fallback note stays a driver-local current-master gap-note companion in this runtime.

## Degraded Validation Path

If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the directly readable validator-side support bundle explicit before the attached-Zig rerun vocabulary:

1. `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
2. `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
3. `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`
4. `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`
5. `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`
6. `python3 scripts/zigux/validate-phase12.py`
7. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
8. attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
9. attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-test ZIG=<attached-zig-path>`
10. attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12 ZIG=<attached-zig-path>`

Do not invent a focused libbpf-only replay, a cross-build replay, or another unshipped closure route while using the degraded path.

## Re-Read Before Changing Closure State

Before changing this checklist from open to closed, reread these files together:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `zigux/tests/README.md`

## Next Bounded Step

If the shared Phase 12 PMO packet drifts again, reread this checklist beside the shared release companions, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, current `zigux/Makefile`, the shared checker pair, and `.github/workflows/zigux-bootstrap.yml`, then refresh only the next smallest release-owned reminder or checker surface that understates the directly readable support bundle, the shipped `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper set, or the docs-root and tests-root shared build gate.

Fresh repo-first rereads now keep the review-checklist fallback and validator-bundle checker hardening current on `master`, so future same-lane follow-through should not loop back into that already-landed repair.

The next honest same-lane follow-through is therefore reminder-side only: leave this checklist parked unless `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, or `zigux/tests/README.md` understates the directly readable support bundle, the shipped `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper set, or the six-file shared `virtio_net` packet.

If only `Documentation/zigux/phase12-raw-github-coverage-survey.md` needs exact readback evidence refresh, leave this checklist parked and let the neighboring `complex-drivers-infra` lane absorb that fallback-only follow-through.

## Non-Goals

- This checklist does not close the Phase 12 tranche by itself.
- This checklist does not widen Phase 12 into new driver implementation work.
- This checklist does not change the freeze-map posture.
- This checklist does not promote driver-local or parked libbpf evidence into the shared replay route.
