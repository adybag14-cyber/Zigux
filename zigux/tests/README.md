# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * `zigux/tests/atomic64_diff.zig`
  * `zigux/tests/runtime_atomic64_diff.zig`
  * `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
  * `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  * `zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-runtime-atomic64-diff-survey`
  * `zigux/tests/bitmap_diff.zig`
  * `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-bitmap-diff`
  * `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * `zigux/tests/phase4_bitmap_diff_manifest.json`
  * `zigux/tests/phase4_bitmap_diff_survey.zig`
  * `zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-bitmap-diff-survey`
  * `zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-bitmap-live-helper-replay`
  * `zigux/tests/phase4_perf_baseline_manifest.json`
  * `zigux/tests/phase4_perf_baseline_survey.zig`
  * `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-perf-baseline-survey`
  * keep the dedicated Phase 4 perf-baseline packet explicit here too: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig`, and `make -C zigux phase4-perf-baseline-survey` keep the approved local-only benchmark commands and acceptable limits explicit while shared CI perf promotion stays pending
  * `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
  * `zigux/tests/phase4_kprobe_example_manifest.json`
  * `zigux/tests/phase4_kprobe_example_survey.zig`
  * `zig test zigux/tests/phase4_kprobe_example_survey.zig`
  * `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
  * `zigux/tests/phase4_test_fsmount_manifest.json`
  * `zigux/tests/phase4_test_fsmount_survey.zig`
  * `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
  * `make -C zigux phase4-test-fsmount-survey`
  * `make -C zigux phase4-kprobe-example-survey`
  * `scripts/zigux/validate-phase4.py`
  * `scripts/zigux/check-artifact-diff-contract.py`
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `scripts/zigux/check-phase4-gate-evidence.py`
  * `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  * `scripts/zigux/check-phase4-workflow-route-counts.py`
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * `zigux/tests/phase4_build.zig`
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
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `samples/zigux/trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample_manifest.json`
  * `zigux/tests/phase5_trace_events_sample_survey.zig`
  * current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase1_helpers.zig`
  * `zigux/tests/phase1_bench.zig`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_bench_expectations.json`
  * current Phase 1 review-and-replay stack: `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`
  * current public-tree-backed Phase 1 parity packet: `zigux/tests/fixtures/phase1_helpers.json` and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * `zigux/tests/phase6_build.zig`
  * `zigux/tests/phase6_helper_parity_manifest.json`
  * `Documentation/zigux/phase6-helper-parity-catalog.md`
  * `Documentation/zigux/phase6-perf-gate-survey.md`
  * `Documentation/zigux/README.md`

Phase 2 review packet
  * `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  * `Documentation/zigux/phase2-closure.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase2.py`
  * `scripts/zigux/validate-phase2-closure.py`
  * `scripts/zigux/check-phase2-tests-readme-alignment.py`
  * `scripts/zigux/check-phase2-kconfig-readme-alignment.py`
  * `scripts/zigux/check-phase2-tool-manifest-packets.py`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py`
  * `scripts/zigux/check-genksyms-bridge.py`
  * `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
  * `scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py`
  * `scripts/zigux/check-phase2-fixdep-gate.py`
  * `scripts/zigux/check-kconfig-bridge.py`
  * `scripts/zigux/check-phase2-cross.py`
  * `scripts/zigux/check-phase2-cross-selftest-alignment.py`
  * `zigux/tests/fixtures/phase2_cross_targets.json`
  * `zigux/tests/fixtures/phase2_tool_manifest.json`
  * `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
  * `zigux/tests/fixtures/genksyms_bridge/manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * `scripts/zigux/kconfig/conf_bridge.zig`
  * `scripts/zigux/kconfig/confdata_bridge.zig`
  * `python3 scripts/zigux/install-zig.py --self-test`
  * `python3 scripts/zigux/check-zig-toolchain.py --self-test`
  * `zig test scripts/zigux/fixdep.zig`
  * `make -C zigux phase2-toolchain`
  * `make -C zigux phase2-validate`
  * `make -C zigux phase2-tools`
  * `make -C zigux phase2-kconfig`
  * `make -C zigux phase2-cross`
  * `make -C zigux phase2`
  * the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset
  * keep the shipped genksyms bridge direct replay visible in the tests root through the committed fixture packet instead of reviving a direct tests-root replay command

Phase 3 review packet
  * `Documentation/zigux/phase3-abi-slice.md`
  * `Documentation/zigux/phase3-abi-bindings-survey.md`
  * `Documentation/zigux/phase3-bindings-governance.md`
  * `Documentation/zigux/phase3-boundary-lane-sequencing.md`
  * `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
  * `Documentation/zigux/phase3-kernel-export-shim-governance.md`
  * `Documentation/zigux/phase3-linux-zigux-header-governance.md`
  * `Documentation/zigux/phase3-abi-header-family-survey.md`
  * `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
  * `Documentation/zigux/phase3-validator-support-surface.md`
  * `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
  * `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
  * `include/zigux/abi.h`
  * `include/zigux/dev_t.h`
  * `include/linux/zigux.h`
  * `zigux/bindings/abi.zig`
  * `zigux/bindings/dev_t.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/layout_assert.zig`
  * `zigux/kernel/export_shim.zig`
  * `zigux/uapi/version.zig`
  * `zigux/uapi/dev_t.zig`
  * `zigux/tests/phase3_abi.zig`
  * `zigux/tests/phase3_abi_dump.zig`
  * `zigux/tests/phase3_export_uapi_layout.zig`
  * `zigux/tests/phase3_export_uapi_layout_build.zig`
  * `zigux/tests/phase3_low_level_wrappers.zig`
  * `zigux/tests/phase3_low_level_wrappers_build.zig`
  * `zigux/tests/fixtures/phase3_abi_manifest.json`
  * `scripts/zigux/validate-phase3.py`
  * `scripts/zigux/validate_phase3_selftest.py`
  * `scripts/zigux/check-phase3-selftest-surface.py`
  * `scripts/zigux/check-phase3-readme-tooling-inventory.py`
  * `scripts/zigux/check-phase3-abi-dump-gate.py`
  * `scripts/zigux/check-phase3-catalog-selftest.py`
  * `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
  * `scripts/zigux/validate-phase3-export-uapi-survey.py`
  * `scripts/zigux/validate-phase3-abi-header-family-survey.py`
  * `scripts/zigux/validate-phase3-validator-support-surface.py`
  * `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
  * `scripts/zigux/survey-phase3-abi-constant-parity.py`
  * `python3 scripts/zigux/validate-phase3.py`
  * `python3 scripts/zigux/validate-phase3.py --slug abi`
  * `python3 scripts/zigux/run-phase3-checks.py --slug abi`
  * `zig build phase3-test --build-file zigux/tests/build.zig`
  * `zig build phase3-dump --build-file zigux/tests/build.zig`
  * `make -C zigux phase3-validate`
  * `make -C zigux phase3-selftest`
  * `make -C zigux phase3`
  * the shared ABI substrate now stays explicit in this tests-root guide through the dedicated ABI-and-bindings survey, the dedicated bindings-governance note, the broader ABI slice note, the adjacent export/UAPI and Linux-facing header-governance notes, the validator-support packet, and the direct `phase3_abi` plus `phase3_abi_dump` replay routes instead of forcing reviewers to reconstruct that packet from the docs root and scripts root alone
  * the focused export/UAPI and low-level-wrapper support routes stay explicit here too: `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, `make -C zigux phase3-export-uapi-layout-test`, `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`, and `make -C zigux phase3-low-level-wrappers-test`
  * `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, and `zigux/uapi/dev_t.zig` stay explicit as the current starter header-family companion packet rather than implying a broader shipped UAPI family

Phase 9 review packet
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase9-build-only-surface.py`
  * `zigux/kernel/runtime_loader.zig`
  * `zigux/kernel/runtime_loader_contract.zig`
  * `zigux/tests/runtime_loader_allocator_init_flow.zig`
  * `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
  * `zigux/tests/runtime_loader_lifecycle_boundary_guard.zig`
  * `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
  * `zigux/tests/runtime_loader_gap_manifest.json`
  * `zigux/tests/runtime_loader_gap_survey.zig`
  * `zigux/tests/runtime_atomic64_manifest.json`
  * `zigux/tests/runtime_bitmap_manifest.json`
  * `zigux/tests/runtime_trace_events_manifest.json`
  * `zigux/tests/runtime_kretprobe_manifest.json`
  * `zigux/tests/runtime_atomic64_survey.zig`
  * `zigux/tests/runtime_bitmap_survey.zig`
  * `zigux/tests/runtime_trace_events_survey.zig`
  * `zigux/tests/runtime_kretprobe_survey.zig`
  * `zigux/tests/phase9_build.zig`
  * `make -C zigux phase9-runtime-loader-shared-tests`
  * `make -C zigux phase9-test`
  * `make -C zigux phase9`
  * `make -C zigux phase9-runtime-atomic64-test`
  * `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`
  * `make -C zigux phase9-runtime-bitmap-top-bit-test`
  * `make -C zigux phase9-runtime-trace-events-test`
  * `make -C zigux phase9-runtime-kretprobe-test`
  * keep the shared Phase 9 tests-root packet aligned around the shipped runtime-loader facade, runtime-loader contract, allocator/init-flow replay, selftest-complete exit parity replay, lifecycle-boundary guard, trace-events loader-substrate-drift proof, and loader-gap manifest-backed survey gate while `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the owner of the exact shared-loader target list, convenience-target names, and the still-blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest boundary instead of leaving that owner map implicit in the tests root
  * there is no dedicated shared `validate-phase9.py` on current `master`; keep the build-only checker plus the literal shared and family-local replay routes above explicit instead of inventing a broader shared validator surface
  * keep the older non-owner boundaries explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence

Phase 10 flow
  * `Documentation/zigux/phase10-closure-evidence.md`
  * `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  * `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  * `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
  * `scripts/zigux/check-phase10-harness-coverage.py`
  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_core_reset_queue.zig`
  * `zigux/tests/phase10_virtio_core_survey.zig`
  * `zigux/tests/phase10_virtio_core_manifest.json`
  * `zigux/tests/phase10_virtio_driver_id.zig`
  * `zigux/tests/phase10_virtio_ring.zig`
  * `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_ring_manifest.json`
  * `zigux/tests/phase10_virtio_input_probe_preflight.zig`
  * `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  * `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  * `zigux/tests/phase10_virtio_input_teardown_observation.zig`
  * `zigux/tests/phase10_virtio_input_status_drain.zig`
  * `zigux/tests/phase10_virtio_input_manifest.json`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/tests/phase10_virtio_mmio_manifest.json`
  * `make -C zigux phase10-validate`
  * `zig build test --build-file zigux/tests/phase10_build.zig --summary all`
  * `make -C zigux phase10-test`
  * `make -C zigux phase10`
  * keep the shared Phase 10 tests-root packet aligned around the direct core, ring, input probe-preflight, queue-callback-preflight, registration-preflight, teardown-observation, status-drain, and MMIO review surfaces while the broader helper names and risky-transport claims stay documented through the closure-manifest-backed reminder notes rather than direct parity claims

Phase 11 review packet
  * `Documentation/zigux/phase11-shared-replay-contract.md`
  * `Documentation/zigux/phase11-closure-note.md`
  * `Documentation/zigux/phase11-driver-lane-sequencing.md`
  * `scripts/zigux/check-phase11-shared-replay-contract.py`
  * `scripts/zigux/check-phase11-shared-summary-surfaces.py`
  * `scripts/zigux/check-phase11-build-inventory.py`
  * `zigux/tests/fixtures/phase11_build_inventory.json`
  * `zigux/tests/phase11_build.zig`
  * `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
  * `make -C zigux phase11-contract`
  * `make -C zigux phase11`
  * `make -C zigux phase11-hvc-survey`
  * surviving DesignWare continuity stays explicit through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
  * dedicated HVC archival packet stays explicit through `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `scripts/zigux/check-phase11-hvc-survey-packet.py`
  * there is no shared `validate-phase11.py` or `make -C zigux phase11-validate` route on current `master`

Phase 12 review packet
  * `scripts/zigux/check-build-only-phase12-surface.py`
  * `Documentation/zigux/phase12-release-sequencing.md`
  * `Documentation/zigux/phase12-release-closure-checklist.md`
  * `Documentation/zigux/phase12-release-readiness-survey.md`
  * `Documentation/zigux/phase12-release-coordination-matrix.md`
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  * `make -C zigux phase12-validate`
  * the shipped validator-first support bundle is `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-cross.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, and it should stay explicit here as support-bundle evidence rather than a second direct replay route
  * `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  * `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  * `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  * `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  * `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  * `Documentation/zigux/phase12-virtio-net-survey.md`
  * `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
  * `scripts/zigux/check-phase12-release-readiness-packet.py`
  * while the direct `virtio_net` starter packet now stays explicit through `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig`
  * current `zigux/tests/phase12_build.zig` also runs `zigux/tests/phase12_virtio_net_transmit_recycle.zig` and `zigux/tests/phase12_virtio_net_queue_resume.zig` in both `smoke` and `test`, but those stay framed as bounded transmit-disposition and queue-resume reviewability rather than live DMA or queue-restart parity
  * `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`
  * `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json`
  * `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  * `make -C zigux phase12-smoke`
  * `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  * `make -C zigux phase12`
  * if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, rerun only the shipped Make routes as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` rather than inventing another Phase 12 route

Phase 13 review packet
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
  * `Documentation/zigux/phase13-release-coordination-matrix.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `fs/libfs.zig`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `lib/devres.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `zigux/tests/phase13_devres_manifest.json`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `scripts/zigux/check-phase13-devres-packet-alignment.py`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  * `scripts/zigux/check-phase13-notifier-priority-signal.py`
  * `scripts/zigux/check-phase13-shared-summary-surfaces.py`
  * `scripts/zigux/validate-phase13-release.py`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/notifier_chain_view.zig`
  * `include/zigux/abi.h`
  * `drivers/tty/hvc/hvc_console.h`
  * `make -C zigux phase13-validate`
  * blocked convenience route `make -C zigux phase13`
  * current `master` now materializes the bounded `libfs`, `devres`, and Landlock helper packets plus the adjacent notifier evidence above, so this tests-root reminder should keep those shipped surfaces explicit instead of collapsing the active Phase 13 packet into a generic future-work summary
  * current `master` still does not materialize `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, older `scripts/zigux/check-phase13-devres-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, or `zigux/helpers/hlist_view.zig`, so keep those paths framed as repo-reality gaps instead of shipped evidence
  * keep `scripts/zigux/check-phase13-shared-summary-surfaces.py` and `make -C zigux phase13-validate` explicit as the stable contributor-facing shared-summary guard plus replay handle; `zigux/Makefile` still exposes `make -C zigux phase13`, but that broader convenience route fans out to `phase13-test`, which still calls `zig build test --build-file zigux/tests/phase13_build.zig --summary all` while `zigux/tests/phase13_build.zig` remains absent on current `master`