# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 1

- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader closure-validator packet from older missing routes
- `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the bounded Phase 1 reminder checks
- `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/check-phase1-direct-owner-markers.py` keep the shipped installer-backed workflow-viability, companion-surface, string-review, and direct-owner marker packet explicit from the scripts root
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet
- repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those older closure-side and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts

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