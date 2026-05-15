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
  * `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * `zigux/tests/phase4_build.zig`
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `samples/zigux/bytestream_fifo.zig`
  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
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
  * current public-tree Phase 5 shared-build gap: `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase1_helpers.zig`
  * `zigux/tests/phase1_bench.zig`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_bench_expectations.json`
  * `zigux/tests/phase6_build.zig`
  * `zigux/tests/phase6_helper_parity_manifest.json`
  * `Documentation/zigux/phase6-helper-parity-catalog.md`
  * `Documentation/zigux/phase6-perf-gate-survey.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase6-shared-surface.py`
  * `zigux/tests/phase6_base64.zig`
  * `zigux/tests/phase6_base64_c_parity.zig`
  * `zigux/tests/phase6_base64_perf.zig`
  * `zigux/tests/fixtures/phase6_base64_vectors.zig`
  * `zigux/tests/fixtures/phase6_base64_c_harness.c`
  * `scripts/zigux/check-phase6-base64-c-parity.py`
  * `zigux/tests/phase6_bsearch.zig`
  * `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
  * `zigux/tests/phase6_bsearch_c_abi_budget.zig`
  * `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
  * `zigux/tests/phase6_checksum_c_parity.zig`
  * `zigux/tests/fixtures/phase6_checksum_c_harness.c`
  * `scripts/zigux/check-phase6-checksum-c-parity.py`
  * `zigux/tests/phase6_hexdump.zig`
  * `zigux/tests/phase6_hexdump_perf.zig`
  * `zigux/tests/phase6_hexdump_perf_matrix.zig`
  * `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`
  * current public-tree Phase 6 gaps: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
  * `zigux/tests/phase7_build.zig`
  * `zigux/tests/phase7_string_helpers.zig`
  * `zigux/tests/phase7_string_helpers_survey.zig`
  * `zigux/tests/phase7_string_helpers_manifest.json`
  * `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  * `zigux/tests/phase7_cmdline.zig`
  * `zigux/tests/phase7_cmdline_survey.zig`
  * `zigux/tests/phase7_cmdline_manifest.json`
  * `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
  * `zigux/tests/phase7_argv_split.zig`
  * `zigux/tests/phase7_argv_split_survey.zig`
  * `zigux/tests/phase7_argv_split_manifest.json`
  * `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  * `zigux/tests/phase7_rbtree.zig`
  * `zigux/tests/phase7_rbtree_survey.zig`
  * `zigux/tests/phase7_rbtree_manifest.json`
  * `zigux/tests/fixtures/phase7_rbtree.json`
  * `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

Phase 8 flow

  * `zigux/tests/phase8_build.zig`
  * `Documentation/zigux/phase8-help-slice.md`
  * `Documentation/zigux/phase8-kallsyms-slice.md`
  * `Documentation/zigux/phase8-tooling-lane-sequencing.md`
  * `zigux/tests/phase8_exec_cmd.zig`
  * `zigux/tests/phase8_exec_cmd_only_build.zig`
  * `zigux/tests/phase8_help.zig`
  * `zigux/tests/phase8_help_only_build.zig`
  * `zigux/tests/phase8_help_kallsyms_only_build.zig`
  * `zigux/tests/phase8_kallsyms.zig`
  * `zigux/tests/phase8_kallsyms_only_build.zig`
  * `zigux/tests/phase8_cpu_mask.zig`
  * `zigux/tests/phase8_cpu_mask_only_build.zig`
  * `zigux/tests/phase8_logging.zig`
  * `zigux/tests/phase8_pin_path.zig`
  * `zigux/tests/phase8_bpf_type_names.zig`
  * `zigux/tests/phase8_file_path_handle_bridge.zig`
  * `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  * `zigux/tests/phase8_perf_buffer_poll.zig`
  * `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  * `zigux/tests/phase8_libbpf_segments.zig`
  * `zigux/tests/phase8_libbpf_segments_only_build.zig`
  * `scripts/zigux/check-phase8-tests-readme-alignment.py`
  * `scripts/zigux/check-phase8-exec-cmd-packet.py`
  * `scripts/zigux/check-phase8-help-kallsyms-packet.py`
  * `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
  * `scripts/zigux/check-phase8-libbpf-segment-gate.py`
  * `scripts/zigux/check-phase8-libbpf-shard-routes.py`
  * `make -C zigux phase8-validate`
  * `make -C zigux phase8-exec-cmd-test`
  * `make -C zigux phase8-help-test`
  * `make -C zigux phase8-help-kallsyms-test`
  * `make -C zigux phase8-kallsyms-test`
  * `make -C zigux phase8-cpu-mask-test`
  * `make -C zigux phase8-file-path-handle-bridge-test`
  * `make -C zigux phase8-libbpf-segments-test`
  * `make -C zigux phase8-perf-buffer-poll-test`
  * `make -C zigux phase8-test`
  * `make -C zigux phase8`

Phase 9 flow

  * `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `scripts/zigux/check-phase9-build-only-surface.py`
  * `zigux/kernel/runtime_loader.zig`
  * `zigux/kernel/runtime_loader_contract.zig`
  * `zigux/tests/runtime_loader_allocator_init_flow.zig`
  * `zigux/tests/runtime_loader_gap_manifest.json`
  * `zigux/tests/runtime_loader_gap_survey.zig`
  * `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
  * `zigux/tests/phase9_build.zig`
  * `zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig`
  * `make -C zigux phase9-runtime-loader-shared-tests`
  * `make -C zigux phase9-runtime-trace-events-test`
  * `make -C zigux phase9-test`
  * `make -C zigux phase9`
  * `zigux/tests/runtime_atomic64_survey.zig`
  * `zigux/tests/runtime_bitmap_survey.zig`
  * `zigux/tests/runtime_trace_events_survey.zig`
  * `zigux/tests/runtime_kretprobe_survey.zig`

Phase 10 flow

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
  * `zigux/tests/phase10_virtio_input.zig`
  * `zigux/tests/phase10_virtio_input_probe_preflight.zig`
  * `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  * `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  * `zigux/tests/phase10_virtio_input_teardown_observation.zig`
  * `zigux/tests/phase10_virtio_input_status_drain.zig`
  * `zigux/tests/phase10_virtio_input_survey.zig`
  * `zigux/tests/phase10_virtio_input_manifest.json`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/tests/phase10_virtio_mmio_manifest.json`
  * `zigux/tests/phase11_build.zig`
  * `zigux/tests/phase11_gpio_wdt.zig`
  * `zigux/tests/phase11_gpio_wdt_manifest.json`
  * `zigux/tests/phase11_gpio_wdt_survey.zig`
  * `zigux/tests/phase11_bcm2835_wdt.zig`
  * `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  * `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  * `zigux/tests/phase11_dw_wdt.zig`
  * `zigux/tests/phase11_dw_wdt_manifest.json`
  * `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
  * `zigux/tests/phase11_dw_wdt_survey.zig`
  * `zigux/tests/phase11_hvc_console.zig`
  * `zigux/tests/phase11_hvc_cleanup.zig`
  * `zigux/tests/phase11_hvc_console_manifest.json`
  * `zigux/tests/phase11_hvc_console_survey.zig`
  * `zigux/tests/phase11_uapi_header_parity_manifest.json`
  * `zigux/tests/phase11_uapi_header_parity_survey.zig`
  * `zigux/tests/phase12_build.zig`
  * `scripts/zigux/check-build-only-phase12-surface.py`
  * `Documentation/zigux/phase12-release-sequencing.md`
  * `Documentation/zigux/phase12-release-closure-checklist.md`
  * `Documentation/zigux/phase12-release-readiness-survey.md`
  * `Documentation/zigux/phase12-release-coordination-matrix.md`
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  * `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  * `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  * `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  * `scripts/zigux/check-phase12-release-readiness-packet.py`
  * `make -C zigux phase12-validate`
  * `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  * `make -C zigux phase12-smoke`
  * `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  * `make -C zigux phase12`
  * `zigux/tests/phase12_virtio_scsi.zig`
  * `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
  * `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`
  * `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
  * `zigux/tests/phase12_virtio_scsi_packet.zig`
  * `zigux/tests/phase12_virtio_scsi_manifest.json`
  * `zigux/tests/phase12_virtio_scsi_survey.zig`
  * `Documentation/zigux/phase12-virtio-scsi-slice.md`
  * `Documentation/zigux/phase12-virtio-scsi-survey.md`
  * `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  * `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  * `Documentation/zigux/phase12-virtio-net-survey.md`
  * `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * `zigux/tests/phase3_abi.zig`
  * `zigux/tests/phase3_low_level_wrappers.zig`
  * `zigux/tests/phase3_abi_dump.zig`
  * `zigux/tests/fixtures/phase3_abi/expected.json`
  * `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
  * `zigux/tests/phase14_build.zig`
  * `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  * `zigux/tests/phase14_workqueue_reviewability.zig`
  * `zigux/tests/phase14_workqueue_bridge_manifest.json`
  * `zigux/tests/phase14_skbuff_bridge_manifest.json`
  * `zigux/tests/phase14_ring_buffer_manifest.json`
  * `zigux/tests/phase14_rcu_tree_manifest.json`
  * `zigux/tests/phase14_ring_buffer_survey.zig`
  * `zigux/tests/phase14_rcu_tree_survey.zig`
  * `zigux/tests/phase14_skbuff_bridge.zig`
  * `zigux/tests/phase14_workqueue_bridge.zig`
  * `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  * `zigux/tests/phase15_build.zig`
  * `zigux/tests/phase15_freeze_map_governance.zig`
  * `zigux/tests/phase15_parity_scorecard.zig`
  * `zigux/tests/phase15_architecture_council_review_process.zig`
  * `zigux/tests/phase15_indefinite_c_policy.zig`
  * `zigux/tests/phase15_handoff_next_steps.zig`
  * `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
  * `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  * `zigux/tests/phase15_governance_lane_sequencing.zig`
  * `zigux/tests/phase15_readiness_gate.zig`
  * `scripts/zigux/validate-phase3.py`
  * `scripts/zigux/validate_phase3_selftest.py`
  * `scripts/zigux/phase3_catalog.py --self-test`
  * `scripts/zigux/phase3_check_lib.py --self-test`
  * `scripts/zigux/generate-phase3-check-wrappers.py --check`
  * `scripts/zigux/run-phase3-checks.py`
Phase 3 fixtures
  * each Phase 3 slice keeps its expected JSON and C harness under `zigux/tests/fixtures/phase3_*`
  * manifests may live beside the fixture directory or inside it; the Phase 3 catalog selects the best valid manifest candidate
  * the catalog also discovers the matching dump entrypoint under `zigux/tests/phase3_*_dump.zig`
  * the shared runner now executes slices directly from catalog metadata, and slice docs may point their `PHASE3_INTEROP_GATE` marker at either `run-phase3-checks.py --slug <slug>` or the legacy wrapper command
  * `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-docs` lists the slice docs that still rely on legacy wrapper markers so cleanup work can stay targeted
  * `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-references` lists the remaining concrete wrapper-path mentions outside the slice docs so fixture and policy cleanup stays targeted too
  * wrapper stubs are convenience entrypoints rather than the execution path and may be pruned when the underlying slice disappears

Guidance
  * keep parity fixtures committed and readable
  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface
  * keep `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces
  * keep the active Phase 2 toolchain packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-tool-manifest-packets.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `zig test scripts/zigux/fixdep.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` should continue to keep the pinned `x86_64-linux` bootstrap archive note, the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset, the shipped fixdep workflow gate plus direct fixdep parity surface, the shipped genksyms bridge gate plus its fixture-backed packet, the dedicated kconfig README, selftest-alignment, and bridge guards, the shipped direct kconfig bridge replays, the bounded three-target compile matrix, the shipped tool-manifest packet, and the shared kbuild-facing replay surface reviewable from the tests root instead of leaving the active Phase 2 tranche split across the docs root, closure note, and Makefile alone
  * keep the shipped genksyms bridge direct replay visible in the tests root through the committed fixture packet instead of reviving a direct tests-root replay command
  * prefer discovery-based validation over hard-coded file inventories when adding new Phase 3 slices
  * keep the focused Phase 3 validator-support replay explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/check-phase3-readme-tooling-inventory.py`, `scripts/zigux/check-phase3-abi-dump-gate.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `scripts/zigux/check-phase3-policy-byte-guards.py`, `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`, `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, `scripts/zigux/validate-phase3-validator-support-surface.py`, `scripts/zigux/validate-phase3-abi-bindings-syntax.py`, `scripts/zigux/survey-phase3-abi-constant-parity.py`, `scripts/zigux/phase3_catalog.py --self-test`, `scripts/zigux/phase3_check_lib.py --self-test`, `scripts/zigux/generate-phase3-check-wrappers.py --check`, `scripts/zigux/run-phase3-checks.py --self-test`, `scripts/zigux/run-phase3-checks.py`, `zigux/Makefile`, `python3 scripts/zigux/validate_phase3_selftest.py`, `scripts/zigux/phase3_catalog.py --audit-doc-sync`, and `make -C zigux phase3-selftest` should continue to keep the shared validator-support runner visible as an opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`, keep the canonical `include/zigux/dev_t.h` plus `zigux/uapi/version.zig` starter-companion split explicit there, and keep `zigux/uapi/dev_t.zig` visible as the broader dedicated survey packet's sibling companion
  * keep the shared Phase 4 rollback packet explicit in the tests root too: `scripts/zigux/validate-phase4.py` should continue to rerun `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, and `scripts/zigux/check-phase4-remaining-gap-matrix.py` before the shared `zigux/tests/phase4_build.zig` entrypoint, `zigux/tests/phase4_build.zig` should continue to run `zigux/tests/atomic64_diff.zig` as the roadmap entrypoint beside `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and `zigux/tests/phase4_bitmap_diff_manifest.json`, and `zigux/tests/phase4_bitmap_diff_survey.zig`, the manifest-backed `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` plus `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` handoff should stay reviewable beside that same wrapper gate, the dedicated local-only perf-baseline survey packet `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig`, the dedicated local `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey` should keep the approved local-only benchmark commands and acceptable limits explicit while shared CI perf promotion stays pending, and `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, the adjacent parked `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint, and `make -C zigux phase4-kprobe-example-survey` packet, plus the adjacent parked `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, `zigux/tests/phase4_test_fsmount_survey.zig`, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style wrapper `make -C zigux phase4-test-fsmount-survey` should keep the helper contract, exact-readback packet, rollback owners, wrapper-versus-runtime handoff, the dedicated local kprobe survey wrapper, the dedicated local test_fsmount survey wrappers, and the still-absent `samples/zigux/test_fsmount.zig` boundary explicit from the tests root without cloning the shared replay body or pretending that a shipped Zig starter already exists
  * keep the landed Phase 4 checker inventory explicit in the tests root too: `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/check-phase4-perf-baseline-packet.py` should stay visible beside `scripts/zigux/validate-phase4.py`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `scripts/zigux/README.md` so the host-side artifact-diff contract, deterministic catalog replay, parked-gap lab matrix, and dedicated local-only perf-baseline packet remain reviewable from the tests root without implying shared-CI perf promotion or shipped Zig starter ports
  * keep the landed Phase 5 sample packet truthful to current direct readback: `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, the four Phase 5 survey notes under `Documentation/zigux/`, the directly readable bytestream sample-root anchor `samples/zigux/bytestream_fifo.zig`, the directly readable kobject packet `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, the directly readable kretprobe packet `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, and the directly readable trace-events packet `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` should stay explicit from the tests root without presenting the missing `zigux/tests/phase5_build.zig`, `make -C zigux phase5-test`, `make -C zigux phase5`, or `zigux/tests/phase5_bytestream_fifo*` packet as current direct evidence
  * keep the current Phase 5 bytestream anchor explicit in the tests root through `Documentation/zigux/phase5-kfifo-sample-survey.md` and `samples/zigux/bytestream_fifo.zig`, and do not restate `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig` as current direct evidence until a fresh reread proves those paths returned
  * keep the current narrower Phase 5 `kobject_example` packet explicit in the tests root too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example.zig` should continue to keep `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary, `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward, `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch plus parse-failure visibility while the sample stays registered, `ownershipSummary()` plus sample-owned `runOwnershipReplay()` explicit for the lifecycle packet, `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` show-or-store rejection packet, the unnamed attribute-group shape, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit from the tests root while shared reminders keep `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` framed as current public-tree gaps instead of shipped current-`master` evidence
  * keep the current Phase 5 kretprobe packet explicit in the tests root through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example.zig`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while still keeping `zigux/tests/phase5_build.zig` explicit as the missing shared build route; shared tests-root wording should keep the separate Phase 9 `runtime_kretprobe` family visible without treating that later runtime family as part of the non-runtime Phase 5 packet
  * keep the shared Phase 13 contributor packet explicit in the tests root too: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/helpers/notifier_chain_view.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `drivers/tty/hvc/hvc_console.h`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13` should continue to keep the active contributor-facing shared-helper packet reviewable from the tests root through the shipped libfs, devres, Landlock ruleset, Landlock syscalls, and adjacent notifier evidence surfaces instead of treating that broader tests-root guide as a pending shared-surface follow-up; keep missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` framed as repo-reality gaps rather than shipped current-`master` evidence, while the shipped `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` stay explicit as the current helper-local proof packet