# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * current direct-readback Phase 1 reminder packet:
    `Documentation/zigux/phase1-closure.md`
    `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
    `Documentation/zigux/README.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase1-closure.py`
    `scripts/zigux/check-phase1-string-review-packet.py`
    `scripts/zigux/check-phase1-direct-owner-markers.py`
    `scripts/zigux/check-phase1-bench.py`
    `scripts/zigux/check-phase1-shared-reminder-packet.py`
    `zigux/tests/fixtures/phase1_helper_manifest.json`
  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
  * current direct-readback Phase 2 kconfig bridge packet:
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
  * Phase 2 review packet:
    `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
    `Documentation/zigux/phase2-closure.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase2.py`
    `scripts/zigux/validate-phase2-closure.py`
    `scripts/zigux/check-zig-toolchain.py`
    `scripts/zigux/check-phase2-kbuild-routes.py`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/check-phase2-tests-readme-alignment.py`
    `scripts/zigux/check-phase2-cross-selftest-alignment.py`
    `scripts/zigux/check-phase2-toolchain-pinning.py`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py`
    `scripts/zigux/check-phase2-docs-shared-reminder.py`
    `scripts/zigux/check-phase2-required-make-routes.py`
    `scripts/zigux/install-zig.py`
    `scripts/zigux/check-phase2-cross.py`
    `python3 scripts/zigux/check-zig-toolchain.py --self-test`
    `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
    `python3 scripts/zigux/install-zig.py --self-test`
    `python3 scripts/zigux/check-phase2-cross.py --self-test`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/Makefile`
    `zigux/tests/fixtures/phase2_tool_manifest.json`
    `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
    `zigux/tests/fixtures/phase2_cross_targets.json`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
    `make -C zigux phase2-toolchain`
    `make -C zigux phase2-tools`
    `make -C zigux phase2-kconfig`
    `make -C zigux phase2-cross`
    `make -C zigux phase2-validate`
    `make -C zigux phase2`
    `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster
  * keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet
  * current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket
  * keep the fixture-backed tool-manifest, artifact-tools, cross-target, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

## Phase 3 review packet

Keep the current bounded Phase 3 ABI/runtime tests-root reminder explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `scripts/zigux/check-phase3-selftest-surface.py` explicit as the shared Phase 3 reminder guard instead of letting the tests-root summary drift away from the bounded current-tree packet.

Current `master` keeps the tests-root Phase 3 reminder anchored to one bounded `dev_t` starter packet, one focused helper-local `err_ptr` / `xarray` slice, one focused helper-local policy slice, the returned packet-local export/UAPI survey note and validator, and the focused export/UAPI layout replay pair instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence.

Keep the current starter and helper packet explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `include/zigux/abi.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/abi.zig`, `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, and `scripts/zigux/check-phase3-policy-starter-packet.py`.

Tests-root reminder posture: keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps.

Keep the returned packet-local export/UAPI survey note and validator explicit through `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py`, while `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/phase3_catalog.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` stay explicit as broader repo-reality gaps. `Documentation/zigux/phase3-shared-reminder-gap.md` should remain the tracker for any later shared-summary follow-through, and `scripts/zigux/README.md` should keep scripts-root inventory work separate from this tests-root reminder packet.

## Phase 12 review packet

Keep the current bounded Phase 12 release packet explicit through `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle so the tests-root summary does not undercount the dedicated release-readiness checker.

Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns. Keep the mixed-source build shard explicit through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, and the directly readable scripts-side support bundle instead of inventing a focused libbpf-only replay or another shared route.

Keep the bounded packet split explicit here too: `virtio_net` remains starter-present reviewability, `virtio_scsi` remains the smoke-first and rollback-lab packet, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, and `zigux/tests/phase12_nvme_pci_survey.zig` stay driver-local outside the shared smoke-and-test route, and the shared libbpf packet stays parked behind `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being promoted into a focused shared replay route.

## Phase 13 review packet

Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with that stable handle as supporting shared reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.

Keep `scripts/zigux/check-phase13-shared-summary-surfaces.py` and `scripts/zigux/check-phase13-tests-readme-alignment.py` explicit as the shipped shared-summary and tests-readme alignment companions for that stable handle instead of leaving either checker implicit behind missing Makefile-backed route vocabulary.

Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
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
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Current `master` instead materializes the narrower devres helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `lib/devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, so broader contributor wording should keep the direct DMA-boundary replay, the pure `dmam_alloc_coherent()` planning helper, and the scatterlist packet explicit instead of rebuilding the older missing `zigux/tests/phase13_devres.zig` replay family.

Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `Documentation/zigux/phase13-landlock-syscalls-slice.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, and the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of treating Landlock as docs-only ownership metadata or as a fully returned syscall replay packet.

Current `master` still does not materialize `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json`, so keep those validator-first, broader direct devres replay, missing direct Landlock syscall, and checker names framed as repo-reality gaps rather than shipped tests-root evidence.

Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.

Current `master` also materializes `scripts/zigux/check-phase13-tests-readme-alignment.py`, so keep that alignment companion explicit as shipped tests-root evidence aligned with the stable contributor-facing handle instead of leaving it implicit in broader reminder wording.

Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.

Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.

Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and keep `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.

Keep `zigux/helpers/notifier_chain_view.zig` framed as an adjacent repo-reality gap rather than a shipped shared surface.

Tests-root reviewer prompt:
- Do the contributor workflow guide, the shared-helper sequencing note, the release coordination and release-notes reminder surfaces, the roadmap-traceability note, the shared-summary-gap and notifier-summary-gap notes, the shared review checklist, the contributor-surface sync note, the shipped shared-summary guard, the helper-local `libfs`, `devres`, and Landlock packet anchors, the stable contributor-facing reminder handle, the explicit repo-reality gaps, and the adjacent notifier evidence all stay aligned on the same bounded Phase 13 contributor packet without promoting the missing Phase 13 make routes or notifier-chain helper into shipped tests-root evidence?

## Phase 14 shared smoke packet

Keep the current bounded Phase 14 reminder packet explicit through `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and keep the blob-readable `scripts/zigux/validate-phase14.py` plus the directly readable workqueue reviewability shard explicit as mixed-source evidence rather than missing executable-layer proof.

Keep the directly readable workqueue reviewability shard explicit through `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` so the tests-root reminder records the returned study-only foothold instead of leaving it inside the missing executable-layer bucket.

Current `master` does materialize `zigux/Makefile`, but its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets, so keep the returned file framed as current repo evidence without promoting the older Phase 14 route names into shipped tests-root proof.

Keep the attached-toolchain fallback explicit as packet-local rerun vocabulary rather than current build-backed evidence:
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`

Keep the blob-readable `scripts/zigux/validate-phase14.py` explicit as the current mixed-source validator surface for this packet, and treat checker-local Phase 14 follow-through as separate review-path work until a fresh current-`master` readback returns it directly.

Current `master` still does not materialize `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, or `net/core/skbuff_bridge.zig`, so keep that executable-layer packet framed as a repo-reality gap rather than shipped tests-root evidence until fresh current-tree reads restore it.

Keep the four roadmap-owned anchors explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors, while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors unless a later Architecture Council packet records a status change.

Tests-root reviewer prompt:
- Does the bounded Phase 14 reminder keep the recovered documentation packet, the blob-readable validator surface, the directly readable workqueue reviewability shard, the attached-toolchain rerun vocabulary, the readable current `zigux/Makefile` surface that now exposes shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes while still omitting all `phase14-*` targets, and the still-missing executable-layer gaps aligned without reviving the older `phase14-*` Makefile routes as shipped current-`master` evidence?

## Phase 15 governance packet

Keep the current bounded Phase 15 governance reminder explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.

Keep the directly readable tests-root Phase 15 governance packet explicit through `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, and `zigux/tests/phase15_readiness_gate_manifest.json` so the tests root records the live freeze-map, review-process, parity, indefinite-C, and readiness evidence packet instead of leaving the current governance packet implicit.

Current `master` still does not materialize `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_build.zig`, or `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep those broader validator-first, handoff-manifest, build-route, and lane-owner companions framed as repo-reality gaps rather than shipped tests-root evidence. Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names in the same blocked-route bucket until direct readback proves they have returned.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the freeze map, review process, decision-record template, indefinite-C policy, parity scorecard, readiness packet, handoff note, shared-summary gap note, directly readable Phase 15 Zig and manifest artifacts, and the shipped scripts-side checker set aligned on maintenance-mode truthfulness work without implying any Architecture Council approval for a freeze-map status change or a returned validator-first build packet?