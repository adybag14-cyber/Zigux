# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
    `scripts/zigux/check-phase4-repo-reality-warning.py`
    `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet: authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands
  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `samples/zigux/bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * current public-tree-backed Phase 5 bytestream companions: `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig`
  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
  * current public-tree-backed Phase 5 kobject survey companion: `zigux/tests/phase5_kobject_example_survey.zig`
  * `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  * `samples/zigux/kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`
  * current public-tree-backed Phase 5 kretprobe shared-build companion: `zigux/tests/phase5_build.zig`
  * keep this tests-root reminder aligned with the restored non-runtime kretprobe packet and keep `zigux/tests/phase5_build.zig` framed as companion evidence instead of direct authenticated-contents proof
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
  * current repo-reality warning for the remaining trace-events sample-local companions: authenticated contents reads on current `master` now return missing for `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig`
  * keep this tests-root reminder aligned with those trace-events survey-note and approved-idiom-gap surfaces plus the shared Phase 5 review packet instead of treating those missing trace-events paths as direct tests-root proof until a fresh reread shows they returned
  * `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/README.md`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_helpers.json`
  * current direct-readback Phase 1 reminder packet: `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py`
  * repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * keep current Phase 1 follow-through tied to the live owner-map plus string-review reminder packet instead of reconstructing the broader installer-backed closure-and-replay packet from those older missing installer, closure-side, and replay files and routes alone
  * current direct-readback Phase 6 shared packet: `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/tests/phase6_helper_evidence_manifest.json`
  * repo-reality warning for the broader Phase 6 helper parity and perf packet: repeated authenticated contents reads on current `master` now return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`
  * keep current Phase 6 follow-through tied to those directly readable shared reminder surfaces plus the restored shared build and machine-readable evidence footholds instead of reconstructing the broader helper-local parity and perf packet from older route names alone

Phase 2 review packet
  * `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase2-kbuild-routes.py`
  * `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
  * `scripts/zigux/check-phase2-tests-readme-alignment.py`
  * `scripts/zigux/check-phase2-toolchain-pinning.py`
  * `scripts/zigux/kconfig/conf_bridge.zig`
  * `scripts/zigux/kconfig/confdata_bridge.zig`
  * `zigux/tests/fixtures/phase2_cross_targets.json`
  * `zigux/tests/fixtures/phase2_tool_manifest.json`
  * `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild and toolchain reminder set plus the live kconfig bridge helpers and their fixture roster; keep this tests-root summary aligned to that narrower packet instead of rebuilding the older validator-first, cross-route, and make-route stack from missing current-`master` paths
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-zig-toolchain.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2`, so keep those route names framed as historical packet members rather than direct tests-root evidence until the files or wrappers return on current `master`
  * keep the fixture-backed cross-target, tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

Phase 3 review packet
  * `Documentation/zigux/phase3-abi-slice.md`
  * `Documentation/zigux/phase3-errptr-xarray-slice.md`
  * `Documentation/zigux/phase3-policy-slice.md`
  * `Documentation/zigux/phase3-validator-support-surface.md`
  * `include/linux/zigux.h`
  * `include/zigux/dev_t.h`
  * `include/zigux/abi.h`
  * `zigux/uapi/version.zig`
  * `zigux/uapi/dev_t.zig`
  * `zigux/bindings/dev_t.zig`
  * `zigux/bindings/abi.zig`
  * `zigux/helpers/err_ptr.zig`
  * `zigux/helpers/xa_value.zig`
  * `zigux/helpers/panic_policy.zig`
  * `zigux/helpers/allocator_policy.zig`
  * `zigux/helpers/unsafe_policy.zig`
  * `zigux/tests/phase3_dev_t_starter_packet.zig`
  * `zigux/tests/phase3_dev_t_starter_packet_build.zig`
  * `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
  * `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
  * `zigux/tests/phase3_policy_starter_packet.zig`
  * `zigux/tests/phase3_policy_starter_packet_build.zig`
  * `zigux/tests/phase3_policy_starter_packet_manifest.json`
  * `scripts/zigux/check-phase3-dev-t-starter-packet.py`
  * `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
  * `scripts/zigux/check-phase3-policy-starter-packet.py`
  * `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
  * `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
  * `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
  * keep the current shared Phase 3 reminder anchored to the bounded `dev_t` starter packet, the helper-local `err_ptr` / `xarray` slice, and the focused policy slice already described in `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, and `Documentation/zigux/phase3-policy-slice.md`, instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence
  * treat broader routes such as `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `scripts/zigux/validate-phase3.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `scripts/zigux/phase3_catalog.py` as repo-reality gaps until fresh current-tree proof lands
  * keep the remaining broader shared-summary follow-up in `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` separate, because those two shared reminder surfaces still need the same three-slice narrowing pass after this tests-root packet is truthful again

Phase 7 review packet
  * current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`
  * repo-reality warning for the broader Phase 7 rbtree packet:
    `Documentation/zigux/phase7-helper-lane-sequencing.md`
    `Documentation/zigux/phase7-rbtree-slice.md`
    `scripts/zigux/check-phase7-rbtree-parity.py`
    `zigux/tests/phase7_rbtree.zig`
    `zigux/tests/phase7_rbtree_manifest.json`
    `zigux/tests/fixtures/phase7_rbtree.json`
    `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
    `zigux/tests/phase7_build.zig`
  * treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again
  * keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone
  * leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree, even if older helper packet references still mention `scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_manifest.json`

Phase 8 review packet
  * current direct-readback Phase 8 anchors:
    `scripts/zigux/check-phase8-tests-readme-alignment.py`
    `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
    `zigux/tests/phase8_perf_buffer_poll.zig`
  * repo-reality warning for the broader Phase 8 tooling packet:
    `Documentation/zigux/phase8-tooling-lane-sequencing.md`
    `Documentation/zigux/phase8-help-slice.md`
    `Documentation/zigux/phase8-kallsyms-slice.md`
    `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
    `Documentation/zigux/phase8-libbpf-segment-survey.md`
    `scripts/zigux/validate-phase8.py`
    `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
    `zigux/tests/phase8_libbpf_segments.zig`
    `zigux/Makefile`
    `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  * keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker-and-test packet instead of reconstructing the broader shared tooling packet from older route names alone
  * if future same-lane work rematerializes the missing docs, validator, focused build shard, libbpf segment test, Makefile routes, or the helper-local `perf_buffer_poll.zig` file, refresh this tests-root summary only after rereading the current direct-readback anchors together on current `master`

Phase 9 review packet
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
  * `zigux/tests/README.md`
  * `samples/zigux/runtime_trace_events.zig`
  * the surviving trace-events sample still keeps the roadmap-backed runtime pilot shape concrete by exposing `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking inside `samples/zigux/runtime_trace_events.zig`, so reviewers can still inspect one real runtime-module and selftest-hook surface while the broader shared loader packet remains backlog
  * there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`

Phase 12 review packet
  * `scripts/zigux/check-build-only-phase12-surface.py`
  * `Documentation/zigux/phase12-release-sequencing.md`
  * `Documentation/zigux/phase12-release-closure-checklist.md`
  * `Documentation/zigux/phase12-release-readiness-survey.md`
  * `Documentation/zigux/phase12-release-coordination-matrix.md`
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  * `make -C zigux phase12-validate`
  * `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  * `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  * `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  * `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  * `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  * `Documentation/zigux/phase12-virtio-net-survey.md`
  * `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
  * `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`
  * `scripts/zigux/check-phase12-release-readiness-packet.py`
  * while the direct `virtio_net` starter packet now stays explicit through `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig`
  * `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`
  * `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json`
  * `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  * `make -C zigux phase12-smoke`
  * `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  * `make -C zigux phase12`

Phase 13 review packet
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
  * `Documentation/zigux/phase13-release-coordination-matrix.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `fs/libfs.zig`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `lib/devres.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `zigux/tests/phase13_devres_manifest.json`
  * `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `scripts/zigux/check-phase13-devres-packet-alignment.py`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  * `scripts/zigux/check-phase13-notifier-priority-signal.py`
  * `scripts/zigux/validate-phase13-release.py`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
  * `zigux/tests/README.md`
  * `zigux/helpers/notifier_chain_view.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `include/zigux/abi.h`
  * `drivers/tty/hvc/hvc_console.h`
  * `zigux/Makefile`
  * stable `make -C zigux phase13-validate`
  * blocked convenience route `make -C zigux phase13`
  * keep the shared validator-first release handle anchored to current repo reality: current `master` materializes the bounded `fs/libfs.zig` foothold together with `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`
  * keep the direct devres boundary-evidence replay explicit beside the shared devres packet through `lib/devres.zig`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`
  * keep the helper-owned Landlock evidence explicit through the ownership and syscall-governance notes, the ruleset and syscall slice plus survey notes, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  * keep the adjacent notifier shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit as shipped adjacent evidence without counting them as extra shared replay steps
  * current `master` still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note framed as an adjacent repo-reality gap rather than as shipped tests-root evidence
  * current `master` still does not materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that checker framed as a remaining shared-summary repo-reality gap rather than as shipped tests-root evidence
  * current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`, but that broader convenience route still fans out to `phase13-test`, which calls `zig build test --build-file zigux/tests/phase13_build.zig --summary all` while `zigux/tests/phase13_build.zig` remains a repo-reality gap
  * keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands, and treat the broader `phase13` route as blocked convenience wiring rather than direct shipped current-`master` evidence
  * if direct companions such as `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, or the older `scripts/zigux/check-phase13-devres-packet.py` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence

## Footer
