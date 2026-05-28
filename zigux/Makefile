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
PHONY += phase3-abi-core-packet phase3-list-hlist-starter-packet phase3-list-hlist-dump phase3-idr-slot-starter-packet-test phase3-idr-slot-dump phase3-low-level-wrappers-test phase3-policy-starter-packet-test phase3-policy-dump phase3-policy-unsafe-test phase3-test phase3-dump phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test phase9-test phase11-validate

.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3 phase3-abi-core-packet phase3-list-hlist-starter-packet phase3-list-hlist-dump phase3-idr-slot-starter-packet-test phase3-idr-slot-dump phase3-xarray-slot-starter-packet phase3-xarray-slot-starter-packet-test phase3-xarray-slot-dump phase3-test phase3-dump phase3-policy-dump phase3-policy-unsafe-test phase3-export-uapi-layout phase3-low-level-wrappers phase3-export-uapi-layout-test phase3-low-level-wrappers-test phase3-policy-starter-packet-test phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase6-validate phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-bsearch-perf phase6-checksum-test phase6-checksum-perf-matrix-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-test phase6-hexdump-perf phase6-perf phase7-validate phase7-rbtree-test phase7-rbtree-survey phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test phase9-test phase10-validate phase10-test phase10 phase11-validate phase12-validate phase12-smoke phase12-test phase12-virtio-net-syntax-lab-test phase12 phase14-validate

phase1-route-summary:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py

phase2-toolchain:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py

phase2-tools:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py

phase2-kconfig: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py

phase2-cross:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2-genksyms: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py

phase2-fixdep: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py

phase3-abi-core-packet:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-abi-core-packet --build-file zigux/tests/build.zig

phase3-list-hlist-starter-packet:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig

phase3-list-hlist-dump:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig

phase3-idr-slot-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig

phase3-idr-slot-dump:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig

phase3-xarray-slot-starter-packet:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig

phase3-xarray-slot-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig

phase3-xarray-slot-dump:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig

phase3-export-uapi-layout:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout --build-file zigux/tests/build.zig

phase3-low-level-wrappers:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig

phase3-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig

phase3-dump:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig

phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump

phase3-export-uapi-layout-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig

phase3-low-level-wrappers-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig

phase3-policy-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig

phase3-policy-dump:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig

phase3-policy-unsafe-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig

phase3-export-shim-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig

phase4-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-validator-replays.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-validation-lane-sequencing.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-validation-lane-sequencing.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py

phase4-artifact-diff-contract:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py

phase4-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-live-helper-replay:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig

phase4-test-fsmount-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig

phase4-kprobe-example-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig

phase4: phase4-validate phase4-test

phase6-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase6.py

phase6-base64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-base64-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-bsearch-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-bsearch-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-perf-matrix-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-review:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-route.py
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-perf-matrix-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all

phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf
phase7-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py

phase7-rbtree-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig

phase7-rbtree-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig

phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-libbpf-segment-gate.py

phase8-exec-cmd-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all

phase8-help-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all

phase8-help-kallsyms-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all

phase8-kallsyms-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all

phase8-libbpf-segments-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all

phase8-file-path-handle-bridge-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all

phase8-perf-buffer-poll-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test

phase9-runtime-atomic64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-bitmap-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-shared-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-command-env-boundary-guard-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-trace-events-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-kretprobe-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-first-loadable-runtime-module-parity-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test

phase10-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-bootstrap-route.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-shared-freeze-boundary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-closure-manifest-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py

phase10-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase10: phase10-validate phase10-test

phase11-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_verify_helper_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_preflight_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig

phase12-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-build-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-build-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-cross-compile-smoke.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-cross-compile-smoke.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-snapshot.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-lane-marker.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py

phase12-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12-nvme-pci-direct-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase12-nvme-pci-direct-test --build-file zigux/tests/phase12_nvme_pci_build.zig --summary all

phase12-nvme-pci-survey-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase12-nvme-pci-survey-test --build-file zigux/tests/phase12_nvme_pci_survey_build.zig --summary all

phase12-virtio-net-syntax-lab-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all

phase12-virtio-net-throughput-parity-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-validate phase12-smoke phase12-test
