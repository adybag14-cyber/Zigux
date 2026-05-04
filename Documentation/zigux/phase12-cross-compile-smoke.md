# Phase 12 Cross Compile Smoke

This note records the bounded non-native compile-smoke packet for the current Phase 12 driver tranche.

- roadmap scope: keep existing Phase 12 `virtio_net`, `nvme_pci`, `virtio_scsi`, and bounded libbpf reviewability surfaces parse-valid across approved non-native musl targets without claiming new runtime parity
- compile entrypoint: `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`
- build file: `zigux/tests/phase12_cross_build.zig`
- shared release packet: `Documentation/zigux/phase12-release-readiness-survey.md`
- shared validator path: `python3 scripts/zigux/check-phase12-raw-github-coverage.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/check-phase12-shared-replay-contract.py`, `python3 scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`
- approved targets: `x86_64-linux-musl`, `aarch64-linux-musl`, `riscv64-linux-musl`
- current packet now includes the landed `phase12_virtio_scsi_recovery_state.zig`, `phase12_virtio_net_syntax_lab.zig`, `phase12_virtio_scsi_syntax_lab.zig`, and `phase12_raw_github_coverage_survey.zig` gates in addition to the existing driver and libbpf survey modules
- rollback posture: if this packet drifts, repair the cross-build wiring or remove the stale claim from this note and `Documentation/zigux/phase12-release-readiness-survey.md` before widening any Phase 12 driver implementation work
