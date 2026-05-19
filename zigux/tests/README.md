# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

## Phase 1 shared host-tools packet

  * current direct-readback Phase 1 reminder packet:

- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`

Keep the tests-root reminder aligned with the live owner-map split and the shipped smoke route instead of reviving the older validator-first, parity, bench-route, or replay packet as if it were current direct-readback evidence.

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

That shared smoke route should stay paired with the restored closure-side validator, the direct owner-map and string-review guards, the shipped bench checker, and the committed helper manifest so the tests-root note matches the same bounded Phase 1 packet already named by the docs root, lane-sequencing note, and scripts-root reminder.

  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`

Current `master` still keeps `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` outside the direct-readback packet here, so leave those validator-first, parity, bench-route, harness, and make-wrapper names framed as historical packet members until a fresh reread restores them on current `master`.

  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof

  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

Tests-root reviewer prompt:
- Does the bounded Phase 1 reminder keep the restored closure-side validator, the direct owner-map and string-review guards, the shipped bench checker, the shared reminder checker, the helper manifest, the shipped smoke route, and the historical-warning wording aligned without reopening helper semantics or promoting missing validator-first and make-route surfaces back into current tests-root evidence?

## Phase 2 review packet

Keep the current direct-readback Phase 2 kconfig and genksyms bridge packet:

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`

Keep the current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`

Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.

Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.

current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof

the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, kconfig bridge checker, and genksyms bridge set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster

keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet

current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket

current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder

keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, and genksyms bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

Tests-root reviewer prompt:
- Does the bounded Phase 2 reminder keep the current direct-readback toolchain, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, kconfig bridge, genksyms bridge, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?

## Phase 3 shared substrate packet

Keep the current direct-readback Phase 3 reminder packet:

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

Keep the shared tests-root reminder aligned with the returned starter, helper, policy, export/UAPI survey, layout-replay, and low-level-wrapper packet instead of narrowing Phase 3 evidence back to the older starter-only story.

`zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`

`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`

`zig build phase3-test --build-file zigux/tests/build.zig`

Current `master` keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` explicit beside the shared `zigux/tests/build.zig` routes, so the tests-root packet should keep both the packet-local survey validators and the returned low-level-wrapper replay/build anchor visible without widening Phase 3 into the broader validator-support, catalog-selftest, or header-family surfaces.

Tests-root reviewer prompt:
- Does the bounded Phase 3 reminder keep the starter, helper, policy, export/UAPI survey, layout-replay, and low-level-wrapper packet aligned across `zigux/tests/build.zig`, the packet-local survey validators, and the dedicated low-level-wrapper replay/build anchor without reopening broader shared-validator, catalog-selftest, or header-family claims?

## Phase 4 rollback-readiness packet

Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.

Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py` so the tests-root summary records the narrower current-head repo-reality packet instead of leaving those returned checker surfaces in the missing bucket.

Current `master` keeps the shared Phase 4 rollback packet split rather than absent: `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig` still do not materialize through authenticated contents reads in this runtime, while `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` are directly readable roadmap-backed differential-gate evidence again.

Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`

Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`

current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone

Keep the shared ownership reminder truthful by pointing back to `Documentation/zigux/phase4-reversible-delivery-evidence.md` for the narrower current-head handoff instead of reconstructing the broader validator-and-bitmap packet from older route names alone.

Tests-root reviewer prompt:
- Does the bounded Phase 4 reminder keep the narrower direct-readback handoff, the returned recovered note-and-checker companions, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair explicit while the validator, build, and bitmap replay companions remain repo-reality gaps in this runtime?

## Phase 10 shared virtio closure packet

Keep `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` explicit as the shared Phase 10 tests-root reminder packet.

Keep the returned checker-backed build gate explicit through `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/tests/phase10_build.zig` so the tests-root reminder stays aligned with the same bounded closure packet already named by the docs root, the lane-sequencing note, the shared review companion, and the scripts-root Phase 10 packet.

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Tests-root reviewer prompt:
- Does the shared Phase 10 reminder keep the closure note, lane-sequencing note, shared review companion, tests-root checker, returned validator and closure-manifest packet, and the returned `zigux/Makefile` body plus `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit as the shared build gate without widening into the still-parked risky transport lanes?

## Phase 12 shared release packet

Keep `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit as the shared Phase 12 tests-root reminder packet.

Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle so the tests-root summary does not undercount the dedicated release-readiness checker.

Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.

Keep `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` explicit as the current shared smoke-first build gate, and keep the degraded rerun order honest by relying on the repo-local `.zig-toolchain` fallback in `zigux/Makefile` before the attached-Zig `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` vocabulary.

Keep the bounded packet split explicit here too: `virtio_net` remains starter-present reviewability, `virtio_scsi` remains the smoke-first and rollback-lab packet, and `nvme_pci` stays driver-local outside the shared smoke-and-test route.

Tests-root reviewer prompt:
- Does the shared Phase 12 reminder keep the release-planning companions, the dedicated build-only and readiness checkers, the shipped validator body, the returned `phase12-smoke`, `phase12-test`, and `phase12` wrappers, the reminder-only `phase12-validate` vocabulary, the repo-local `.zig-toolchain` then attached-Zig degraded rerun order, and the bounded `virtio_net` plus `virtio_scsi` plus driver-local NVMe split aligned without widening into DMA, queue restart, throughput, or deeper transport claims?

## Phase 13 review packet

Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with that stable handle as supporting shared reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.

Keep `scripts/zigux/check-phase13-tests-readme-alignment.py` explicit as the shipped tests-root alignment companion for that stable handle rather than as a new replay route or a Makefile-backed entrypoint.

Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `lib/devres.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Current `master` instead materializes the narrower devres helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `lib/devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, so broader contributor wording should keep the direct DMA-boundary replay, the pure `dmam_alloc_coherent()` planning helper, and the scatterlist packet explicit instead of rebuilding the older missing `zigux/tests/phase13_devres.zig` replay family.

Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `Documentation/zigux/phase13-landlock-syscalls-slice.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, and the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of treating Landlock as docs-only ownership metadata or as a fully returned syscall replay packet.

Current `master` still does not materialize `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json`, so keep those validator-first, broader direct devres replay, missing direct Landlock syscall, and checker names framed as repo-reality gaps rather than shipped tests-root evidence.

Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.

Current `master` also materializes `scripts/zigux/check-phase13-tests-readme-alignment.py`, so keep that companion explicit as shipped tests-root evidence aligned with the contributor workflow guide, shared-helper sequencing note, release-coordination matrix, and compact review companion instead of leaving it implicit inside the broader tests-root prose.

Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.

Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.

Keep `zigux/helpers/notifier_chain_view.zig` framed as an adjacent repo-reality gap rather than a shipped shared surface.

Tests-root reviewer prompt:
- Does the bounded Phase 13 reminder keep the stable contributor-facing handle, the shipped tests-root alignment companion `scripts/zigux/check-phase13-tests-readme-alignment.py`, the shipped helper-local `libfs`, `devres`, and Landlock anchors, the shared-summary guard, the adjacent notifier evidence, the returned-but-still-non-owner `zigux/Makefile` file, and the still-missing Phase 13 build-route, validator-first, deeper devres replay, notifier-priority, and Landlock syscall replay surfaces aligned without promoting repo-reality gaps back into shipped tests-root proof?

## Phase 14 shared smoke packet

Keep the current bounded Phase 14 reminder packet explicit through `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and keep the directly readable `scripts/zigux/validate-phase14.py` plus the directly readable workqueue reviewability shard explicit as current shared-smoke evidence rather than missing executable-layer proof.

Keep the directly readable workqueue reviewability shard explicit through `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` so the tests-root reminder records the returned study-only foothold instead of leaving it inside the missing executable-layer bucket.

Keep `scripts/zigux/check-phase14-release-boundary-exact-counts.py` explicit as the directly readable release-boundary truthfulness guard beside the directly readable validator surface and the returned workqueue shard.

Current `master` does materialize `zigux/Makefile`, but its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets, so keep the returned file framed as current repo evidence without promoting the older Phase 14 route names into shipped tests-root proof.

Keep the attached-toolchain boundary explicit only as historical packet-local vocabulary rather than current build-backed evidence while the readable `zigux/Makefile` still omits the matching `phase14-*` targets. Older examples such as `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`, `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`, and `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14` should stay traceability cues only until the same exact readback mode restores both the dedicated Phase 14 build-side files and the `phase14-*` Makefile routes.

Keep the directly readable `scripts/zigux/validate-phase14.py` explicit as the current shared-smoke validator surface for this packet, and treat checker-local Phase 14 follow-through as separate review-path work rather than missing executable-layer proof.

Current `master` still does not materialize `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, or `net/core/skbuff_bridge.zig`, so keep that executable-layer packet framed as a repo-reality gap rather than shipped tests-root evidence until fresh current-tree reads restore it.

Keep the four roadmap-owned anchors explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors, while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors unless a later Architecture Council packet records a status change.

Tests-root reviewer prompt:
- Does the bounded Phase 14 reminder keep the recovered documentation packet, the directly readable validator surface, the directly readable release-boundary truthfulness guard, the directly readable workqueue reviewability shard, the historical attached-toolchain wrapper vocabulary, the readable current `zigux/Makefile` surface that now exposes shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes while still omitting all `phase14-*` targets, and the still-missing executable-layer gaps aligned without reviving the older `phase14-*` Makefile routes as shipped current-`master` evidence?

## Phase 15 shared governance packet

Keep the current directly readable Phase 15 reminder packet explicit through `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_freeze_map_governance.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, and `zigux/tests/phase15_handoff_next_steps_manifest.json`.

Keep the active-governance replay entrypoints explicit here too: `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py`.

Current `master` does materialize `scripts/zigux/check-phase15-readiness-gate-packet.py`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_readiness_gate.zig`, and `zigux/tests/phase15_indefinite_c_policy.zig`, so keep those returned readiness, handoff survey, handoff-manifest, shared-summary, and stay-in-C packet members explicit in the tests-root reminder instead of leaving them in a missing-evidence bucket.

Current `master` still does not materialize `scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, `zigux/tests/phase15_build.zig`, or `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep those validator-first, route-level, build-level, and lane-owner-alignment surfaces framed as repo-reality gaps unless fresh current-tree reads restore them.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the directly readable governance packet, the returned readiness, handoff survey, and handoff-manifest packet members, the shared-summary gap note, the active-governance replay entrypoints, and the still-missing validator-first, route-level, build-level, and lane-owner-alignment surfaces aligned without promoting blocked governance wrappers or deeper-core status changes into current tests-root evidence?
