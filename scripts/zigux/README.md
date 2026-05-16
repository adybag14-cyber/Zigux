# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 11

- Phase 11 flow - the shared replay contract, summary-surface guard, build-inventory guard, and dedicated packet checks keep the current simple-driver packet aligned
- `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `scripts/zigux/check-phase11-build-inventory.py`, `make -C zigux phase11-contract`, and `make -C zigux phase11` keep the shared-versus-dedicated packet explicit
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- the shared build anchor now stays explicit through `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_build.zig`, and `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- the active host-free packet still centers the direct watchdog continuity surfaces plus the HVC teardown, sysrq-helper, verify-helper, cleanup replay, and exported-layout proof surfaces without widening into platform registration execution, notifier callbacks, khvcd execution, live sysrq execution, watchdog-core glue, or host-backed teardown

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