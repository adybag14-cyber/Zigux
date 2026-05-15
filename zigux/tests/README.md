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
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * current public-tree-backed Phase 5 bytestream companions: `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig`
  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
  * `zigux/tests/phase5_kobject_example_survey.zig`
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
  * current public-tree-backed Phase 1 parity packet: `zigux/tests/fixtures/phase1_helpers.json` and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
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
  * current public-tree-backed Phase 6 checksum packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
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
  * `scripts/zigux/check-phase7-argv-split-packet.py`
  * `zigux/tests/phase7_rbtree.zig`
  * `zigux/tests/phase7_rbtree_survey.zig`
  * the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate
  * `zigux/tests/phase7_rbtree_manifest.json`
  * `zigux/tests/fixtures/phase7_rbtree.json`
  * `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  * `scripts/zigux/check-phase7-rbtree-parity.py`
  * `make -C zigux phase7-validate`
  * `make -C zigux phase7`

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

Keep the Phase 9 flow bounded to the shared runtime-loader packet above plus these four Phase 9 survey gates. `Phase 10 flow` and the later inventories below are adjacent later-phase packets, not shared runtime-pilot evidence.

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
  * `scripts/zigux/validate-phase12.py`
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