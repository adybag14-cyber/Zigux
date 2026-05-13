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
  * `scripts/zigux/validate-phase4.py`
  * `Documentation/zigux/phase4-validation-matrix.md`
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
  * keep the focused Phase 3 validator-support replay explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `zigux/uapi/dev_t.zig`, `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/check-phase3-readme-tooling-inventory.py`, `scripts/zigux/check-phase3-abi-dump-gate.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `scripts/zigux/check-phase3-policy-byte-guards.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, `scripts/zigux/validate-phase3-validator-support-surface.py`, `scripts/zigux/validate-phase3-abi-bindings-syntax.py`, `scripts/zigux/survey-phase3-abi-constant-parity.py`, `scripts/zigux/phase3_catalog.py --self-test`, `scripts/zigux/phase3_check_lib.py --self-test`, `scripts/zigux/generate-phase3-check-wrappers.py --check`, `scripts/zigux/run-phase3-checks.py --self-test`, `scripts/zigux/run-phase3-checks.py`, `zigux/Makefile`, `python3 scripts/zigux/validate_phase3_selftest.py`, `scripts/zigux/phase3_catalog.py --audit-doc-sync`, and `make -C zigux phase3-selftest` should continue to keep the shared validator-support runner visible as an opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`
  * keep the shared Phase 4 rollback packet explicit in the tests root too: `scripts/zigux/validate-phase4.py` should continue to rerun `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py` before the shared `zigux/tests/phase4_build.zig` entrypoint, `zigux/tests/phase4_build.zig` should continue to run `zigux/tests/atomic64_diff.zig` as the roadmap entrypoint beside `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, and `zigux/tests/phase4_bitmap_diff_manifest.json`, and `zigux/tests/phase4_bitmap_diff_survey.zig`, the manifest-backed `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` plus `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` handoff should stay reviewable beside that same wrapper gate, the dedicated local-only perf-baseline survey packet `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig`, the dedicated local `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style wrapper `make -C zigux phase4-perf-baseline-survey` should keep the approved local-only benchmark commands and acceptable limits explicit while shared CI perf promotion stays pending, and `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, the adjacent parked `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint, and `make -C zigux phase4-kprobe-example-survey` packet, plus the adjacent parked `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, `zigux/tests/phase4_test_fsmount_survey.zig`, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style wrapper `make -C zigux phase4-test-fsmount-survey` should keep the helper contract, exact-readback packet, rollback owners, wrapper-versus-runtime handoff, the dedicated local kprobe survey wrapper, the dedicated local test_fsmount survey wrappers, and the still-absent `samples/zigux/test_fsmount.zig` boundary explicit from the tests root without cloning the shared replay body or pretending that a shipped Zig starter already exists
  * keep the shared Phase 5 sample packet truthful to current direct readback: `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, the four Phase 5 survey notes under `Documentation/zigux/`, the directly readable bytestream sample-root anchor `samples/zigux/bytestream_fifo.zig`, the directly readable kobject packet `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, the survey-note-only kretprobe anchor `Documentation/zigux/phase5-kretprobe-sample-survey.md`, and the directly readable trace-events packet `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` should stay explicit from the tests root without presenting the missing `zigux/tests/phase5_build.zig`, `make -C zigux phase5-test`, `make -C zigux phase5`, `zigux/tests/phase5_bytestream_fifo*`, or `zigux/tests/phase5_kretprobe_example*` packet as current direct evidence
  * keep the current Phase 5 bytestream anchor explicit in the tests root through `Documentation/zigux/phase5-kfifo-sample-survey.md` and `samples/zigux/bytestream_fifo.zig`, and do not restate `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, or `zigux/tests/phase5_build.zig` as current direct evidence until a fresh reread proves those paths returned
  * keep the current narrower Phase 5 `kobject_example` packet explicit in the tests root too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example.zig` should continue to keep `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary, `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward, `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch plus parse-failure visibility while the sample stays registered, `ownershipSummary()` plus sample-owned `runOwnershipReplay()` explicit for the lifecycle packet, `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` show-or-store rejection packet, the unnamed attribute-group shape, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit from the tests root while shared reminders keep `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` framed as current public-tree gaps instead of shipped current-`master` evidence
  * keep the current Phase 5 kretprobe anchor explicit in the tests root through `Documentation/zigux/phase5-kretprobe-sample-survey.md` only until a fresh reread proves `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_survey.zig`, and `zigux/tests/phase5_build.zig` returned; shared tests-root wording should keep the separate Phase 9 `runtime_kretprobe` family visible without treating those missing non-runtime packet paths as current direct evidence
  * keep the directly readable Phase 5 `trace-events_sample` packet explicit in the tests root too: `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample.zig`, and `zigux/tests/phase5_trace_events_sample_survey.zig` should continue to keep the non-runtime selected-string, `iter=%d`, exact `checked_focus` order, relative-location, vararg-payload, the public `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, and `runCallbackBoundaryReplay()` helpers, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, post-exit replay rejection, and the separate Phase 9 `runtime_trace_events` family visible from the tests root instead of leaving that shipped sample-backed packet implicit or treating the missing `zigux/tests/phase5_build.zig` route as current direct evidence
  * keep the shared Phase 6 leaf-helper packet wired through `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `scripts/zigux/check-phase6-base64-c-parity.py`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, and `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, so the current partially blocked base64, bsearch, checksum, and hexdump bundle stays reviewable through one bounded helper gate, keep `zigux/tests/phase6_hexdump_perf.zig` plus `zigux/tests/phase6_hexdump_perf_matrix.zig` explicit as the live helper-local hexdump perf packet, and keep `zigux/tests/phase6_base64_perf.zig`, `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` explicit as current public-tree gaps rather than shipped tests-root entrypoints or runnable shared perf coverage
  * keep `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` explicit in the tests root too so the committed fixture-backed bsearch, checksum, hexdump, and base64 evidence stays reviewable from the same shared catalog instead of living only inside helper-local imports and slice prose
  * keep the active Phase 10 virtio packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-closure-evidence.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, `make -C zigux phase10-validate`, `zig build test --build-file zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10` should continue to keep the current virtio core, the direct `drivers/virtio/virtio.zig` plus `drivers/virtio/virtio_driver_id.zig` review surfaces, the bounded reset replay, the direct driver-id replay, the direct `drivers/virtio/virtio_ring.zig` ring surface beside `drivers/virtio/virtio_ring_verify.zig` and `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, the lane-sequenced input verify plus probe-preflight, queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays, and the virtio mmio packet plus the focused mmio-verify replay reviewable from the tests root while keeping `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` framed as repo-reality gaps rather than shipped current-`master` evidence
  * keep the shared Phase 11 simple-driver packet explicit in the tests root too: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig --summary all`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` should continue to keep the same shared-versus-dedicated replay split, the dedicated bcm2835 archival checker route, the dedicated DesignWare packet checker, the dedicated bcm2835, gpio, and DesignWare manifest-backed survey checkpoints, the focused header-boundary note plus manifest-backed survey packet, the four driver-local validation matrices, the dedicated gpio teardown companion, the dedicated DesignWare teardown companion, the bounded `hvc_cleanup()` teardown handoff through `zigux/tests/phase11_hvc_cleanup.zig`, the dedicated archival `hvc_console` teardown note plus the direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, manifest-backed survey gate, modem-control split, poll-retry split, and `drivers/tty/hvc/hvc_console_sysrq.zig` sysrq-helper boundary, and the dedicated `phase11-hvc-survey` checker-backed replay route reviewable from the tests root without implying a removed `validate-phase11.py`, a missing build-inventory fixture, or a broader validator stack than the five shipped Phase 11 checker scripts on `master`
  * keep the shared Phase 12 complex-driver packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` should continue to keep the current smoke-first release packet reviewable from the tests root through the workflow-backed build-only contract, while the direct `virtio_net` starter packet now stays explicit through `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig`, the parked libbpf reviewability anchor stays explicit through `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `scripts/zigux/validate-phase12.py` stays support material beside the shipped build-only checker rather than a shared `phase12-validate` route, and the still-absent direct `phase12_nvme_pci` and `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`, without implying removed `check-phase12-*.py`, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces
  * keep the shared Phase 15 governance packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase15.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_readiness_gate.zig`, `zig build test --build-file zigux/tests/phase15_build.zig`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` should continue to keep the parked freeze-map, review-process, parity-scorecard, handoff-next-steps, blocker-evidence, indefinite-C policy, lane-owner alignment, governance-lane sequencing, and readiness-gate packet explicit from the tests root beside the shipped validator-first and replay routes without implying any Architecture Council approval for a freeze-map status change
## Footer
