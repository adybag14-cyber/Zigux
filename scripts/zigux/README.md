# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 1

- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes
- `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test` and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the shipped bounded Phase 1 reminder checks
- `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py` keep the shipped string-review and direct-owner marker packet explicit from the scripts root
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, closure-side, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts

## Phase 4

- Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root and tests-root surfaces while the broader scripts-side validator and local-only perf packet remain repo-reality gaps on current `master`
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the repo-reality warning for the broader validator, lab-matrix, and local-only perf companions, and the pending shared-CI perf-promotion posture explicit
- repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`, so treat those paths as last-known packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` scripts-root evidence
- keep the dedicated local-only perf packet and any broader shared-CI perf-promotion decision owned by the Validation and Perf Team, keep the ABI and Runtime Team plus Shared Subsystems Pod explicit as coordination owners for any wider promotion call, and keep the parked kprobe plus parked `test_fsmount` reminder packet framed as adjacent last-known packet members instead of current direct scripts-root evidence

## Phase 6

- Phase 6 flow - the current shared helper-evidence packet keeps the bounded base64, bsearch, checksum, and hexdump lane truthful from the scripts root without widening into new helper semantics
- `python3 scripts/zigux/check-phase6-shared-surface.py --self-test` and `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test` replay the shipped shared-surface and present-entrypoint guards
- `scripts/zigux/check-phase6-shared-surface.py` and `scripts/zigux/check-phase6-present-entrypoints.py` keep the direct-readback warning, the helper-evidence catalog packet, and the shared replay inventory explicit from the scripts root
- `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/README.md` remain the current reminder-surface companions for that packet
- the shared replay inventory now treats `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-base64-perf`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-checksum-perf` as committed rerun routes beside the existing bsearch and hexdump reminders, so keep those wrappers out of the older inventory-only bucket
- keep the current partially blocked helper packet tied to those shared surfaces instead of reconstructing broader helper-local proof from older route names alone until fresh direct reads recover the missing helper-local replay files again

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

## Phase 13

- Phase 13 flow - `python3 scripts/zigux/validate-phase13-release.py` plus stable `make -C zigux phase13-validate` keep the active shared-helper contributor packet aligned from the scripts root
- `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `python3 scripts/zigux/validate-phase13-release.py` keep the shipped Phase 13 helper-local and adjacent notifier reminder packet explicit without collapsing it into one generic shared note
- `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` are the current broad reminder companions for that packet
- keep helper-local ownership explicit: `fs/libfs.zig` stays the bounded `libfs` foothold, `lib/devres.zig` plus `zigux/tests/phase13_devres_boundary_evidence.zig` stay the devres boundary-evidence packet, `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` stay helper-owned Landlock anchors, and adjacent notifier evidence stays support material instead of a fifth helper family
- current `master` still does not materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that checker framed as the remaining shared-summary repo-reality gap rather than as shipped scripts-root evidence
- current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`, but that broader convenience route still fans out to `phase13-test`, which calls `zig build test --build-file zigux/tests/phase13_build.zig --summary all` while `zigux/tests/phase13_build.zig` remains a repo-reality gap
- keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands, and treat the broader `phase13` route as blocked convenience wiring rather than direct shipped current-`master` evidence
- if direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, or the older `scripts/zigux/check-phase13-devres-packet.py` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence
- if `zig` is unavailable on `PATH`, rerun the shipped validator-first route with `ZIG=<attached-zig-path>` and keep the blocked convenience route wording unchanged until the shared build companion lands