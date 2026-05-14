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
  * `zigux/tests/bitmap_diff.zig`
  * `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * `zigux/tests/phase4_bitmap_diff_manifest.json`
  * `zigux/tests/phase4_bitmap_diff_survey.zig`
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
  * `zigux/tests/phase4_build.zig`
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `samples/zigux/bytestream_fifo.zig`
  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
  * `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `samples/zigux/trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample_manifest.json`
  * `zigux/tests/phase5_trace_events_sample_survey.zig`
  * `zigux/tests/phase1_helpers.zig`
  * `zigux/tests/phase1_bench.zig`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_bench_expectations.json`
  * `zigux/tests/phase6_build.zig`
  * `zigux/tests/phase6_helper_parity_manifest.json`
  * `Documentation/zigux/phase6-helper-parity-catalog.md`
  * `Documentation/zigux/phase6-perf-gate-survey.md`
  * `zigux/tests/phase6_base64.zig`
  * `zigux/tests/phase6_base64_c_parity.zig`
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
  * `scripts/zigux/check-phase8-help-kallsyms-packet.py`
  * `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
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
  * `zigux/tests/phase9_build.zig`
  * `zigux/tests/runtime_atomic64_survey.zig`
  * `zigux/tests/runtime_bitmap_survey.zig`
  * `zigux/tests/runtime_trace_events_survey.zig`
  * `zigux/tests/runtime_kretprobe_survey.zig`
  * `zigux/tests/runtime_loader_allocator_init_flow.zig`
  * `zigux/tests/runtime_loader_gap_survey.zig`
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
