PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
PHASE8_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..
PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json
ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["channel"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)
ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["upgrade_policy"]["archive_target_scope"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)
ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)
ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))
ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)
ZIG_REPO_ROOT := $(if $(ZIG_PINNED_TOOLCHAIN),$(abspath $(ZIG_PINNED_TOOLCHAIN)),$(ZIG))
ZIG_REPO_ROOT_DIR := $(dir $(ZIG_REPO_ROOT))
export PATH := $(ZIG_REPO_ROOT_DIR):$(PATH)
PHONY += phase3-abi-core-packet phase3-abi-export phase3-list-hlist-starter-packet phase3-list-hlist-dump phase3-idr-slot-starter-packet-test phase3-idr-slot-dump phase3-low-level-wrappers-test phase3-policy-starter-packet-test phase3-policy-dump phase3-policy-unsafe-test phase3-test phase3-dump phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test phase9-test phase11-validate
PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4
PHONY += phase10-validate phase10-test phase10

.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3 phase3-abi-core-packet phase3-abi-export phase3-list-hlist-starter-packet phase3-list-hlist-dump phase3-idr-slot-starter-packet-test phase3-idr-slot-dump phase3-xarray-slot-starter-packet phase3-xarray-slot-starter-packet-test phase3-xarray-slot-dump phase3-test phase3-dump phase3-policy-dump phase3-policy-unsafe-test phase3-export-uapi-layout phase3-low-level-wrappers phase3-export-uapi-layout-test phase3-low-level-wrappers-test phase3-policy-starter-packet-test phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase6-validate phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-bsearch-perf phase6-checksum-test phase6-checksum-perf-matrix-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-test phase6-hexdump-perf phase6-perf phase7-validate phase7-rbtree-test phase7-rbtree-survey phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test phase9-test phase10-validate phase10-test phase10 phase11-validate phase12-validate phase12-smoke phase12-test phase12-virtio-net-syntax-lab-test phase12-virtio-net-throughput-parity-test phase12-nvme-pci-direct-test phase12-nvme-pci-survey-test phase12 phase14-validate

phase1-route-summary:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase1_route_summary_counts.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase1_route_summary_counts.zig

phase2-toolchain:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/toolchain_policy.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/toolchain_resolver.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_policy_validation_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_version_evaluation_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_policy_only_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_policy_schema_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_allow_missing_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_archive_only_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_archive_report_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_archive_target_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_executable_failure_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_explicit_archive_path_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_explicit_archive_target_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_explicit_zig_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_repo_local_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_repo_local_priority_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_resolver_priority_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_search_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain_version_status_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/lane03_archive_candidate_ambiguity_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/lane03_toolchain_policy_schema_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/check_zig_toolchain.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/check_zig_toolchain.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/check_zig_toolchain.zig -- --policy-only
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_local_first_archive_workflow.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_local_archive_readme.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_install_zig_archive_verification.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/install_zig.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/install_zig.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/stage_pinned_zig_archive.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/lane03_stage_parts_manifest_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_stage_helper_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_stage_helper_selftest.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_lane05_stage_helper_selftest.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_toolchain_pinning.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_toolchain_pinning.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_toolchain_pin_scope.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_toolchain_pin_scope.zig

phase2-tools:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_kbuild_routes.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_kbuild_routes.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_docs_shared_reminder.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_docs_shared_reminder.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_required_make_routes.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_artifact_tools_manifest.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_artifact_tools_manifest.zig

phase2-kconfig: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/conf_bridge_savedefconfig_mode_arg_escape_surface_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/confdata_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_kconfig_selftest_alignment.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_kconfig_selftest_alignment.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig

phase2-cross:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_cross.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_cross.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_cross_selftest_alignment.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_cross_selftest_alignment.zig

phase2-genksyms: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_inline_short_option_argument_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_genksyms_selftest_alignment.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_genksyms_selftest_alignment.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig

phase2-fixdep: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig -- --zig "$(ZIG_REPO_ROOT)"
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_tests_readme_alignment.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_tests_readme_alignment.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_tool_manifest.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_tool_manifest.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase2_closure.zig

phase2: phase2-validate

phase3-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase3_selftest.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/run_phase3_checks.zig

phase3-abi-core-packet:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-abi-core-packet --build-file zigux/tests/build.zig

phase3-list-hlist-starter-packet:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig

phase3-list-hlist-dump:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig

phase3-idr-slot-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig

phase3-idr-slot-dump:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig

phase3-xarray-slot-starter-packet:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig

phase3-xarray-slot-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig

phase3-xarray-slot-dump:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig

phase3-export-uapi-layout:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout --build-file zigux/tests/build.zig

phase3-abi-export:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-abi-export --build-file zigux/tests/build.zig

phase3-low-level-wrappers:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig

phase3-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-test --build-file zigux/tests/build.zig

phase3-dump:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-dump --build-file zigux/tests/build.zig

phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump

phase3-export-uapi-layout-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig

phase3-low-level-wrappers-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig

phase3-policy-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig

phase3-policy-dump:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig

phase3-policy-unsafe-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig

phase3-export-shim-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig

phase4-validate:
	$(MAKE) phase4-artifact-diff-contract
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_gate_evidence.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_remaining_gap_matrix.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_workflow_route_counts.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_validation_lane_sequencing.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig

phase4-artifact-diff-contract:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/artifact_diff.zig -- --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_text_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_json_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_bytes_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_cli_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_utf8_error_contract.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/artifact_diff_missing_path_contract.zig

phase4-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-live-helper-replay:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig

phase4-test-fsmount-survey:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig

phase4-kprobe-example-survey:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test zigux/tests/phase4_kprobe_example_survey.zig

phase4: phase4-validate phase4-test

phase6-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase6.zig

phase6-base64-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-base64-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-base64-perf:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-bsearch-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-bsearch-perf:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-perf-matrix-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-perf:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-review:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase6_hexdump_packet.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase6_hexdump_route.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-perf-matrix-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-perf:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all

phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf
phase7-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig

phase7-rbtree-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig

phase7-rbtree-survey:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig

phase8-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase8.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase8_libbpf_segment_gate.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase8.zig

phase8-exec-cmd-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all

phase8-help-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all

phase8-help-kallsyms-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all

phase8-kallsyms-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all

phase8-libbpf-segments-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all

phase8-file-path-handle-bridge-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all

phase8-perf-buffer-poll-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all

phase8-test: phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase8_build.zig --summary all

phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test

phase9-runtime-atomic64-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-bitmap-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-shared-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-command-env-boundary-guard-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-trace-events-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-kretprobe-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-first-loadable-runtime-module-parity-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test

phase10-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_bootstrap_route.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_shared_freeze_boundary.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_ring_packet.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_input_packet.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_mmio_packet.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_harness_coverage.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_tests_readme_core_surfaces.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase10_closure_manifest_counts.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase10_closure.zig

phase10-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase10_build.zig --summary all

phase10: phase10-validate phase10-test

phase11-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase11.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_gpio_wdt_verify_helper_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_gpio_wdt_preflight_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig

phase12-validate:
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_build_only_phase12_surface.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_build_inventory.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_release_readiness_packet.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_complex_driver_lane_packet.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_cross_compile_smoke.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_virtio_scsi_libbpf_boundary.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_snapshot.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_lane_marker.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_heavy_consumer_packet.zig
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase12.zig --self-test
	$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase12.zig

phase12-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12-virtio-net-syntax-lab-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all

phase12-virtio-net-throughput-parity-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all

phase12-nvme-pci-direct-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase12-nvme-pci-direct-test --build-file zigux/tests/phase12_nvme_pci_build.zig --summary all

phase12-nvme-pci-survey-test:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase12-nvme-pci-survey-test --build-file zigux/tests/phase12_nvme_pci_survey_build.zig --summary all

phase12: phase12-validate phase12-smoke phase12-test

phase14-validate:
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_shared_smoke_route.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_shared_smoke_route.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_tests_readme_smoke_summary.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase14.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase14.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_rollback_threshold_sequencing.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_rollback_threshold_sequencing.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_rcu_rollback_guardrail.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_rcu_rollback_guardrail.zig
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_release_boundary_exact_counts.zig --self-test
	cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase14_release_boundary_exact_counts.zig
