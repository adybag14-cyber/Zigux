# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 12

- Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned
- `scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` keep the degraded-workflow support bundle explicit
- `check-build-only-phase12-surface.py`
- `Documentation/zigux/phase12-release-sequencing.md`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- the current starter-present `virtio_net` plus smoke-first `virtio_scsi` release packet and the parked verify-shard-backed libbpf survey packet reviewable from the scripts root
- If `zig` is unavailable on `PATH`, rerun only the shipped Make routes with `ZIG=<attached-zig-path>`
