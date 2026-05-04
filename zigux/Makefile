PHONY += phase1-validate phase1-test phase1-bench phase1
PHONY += phase2-validate phase2-tools phase2-kconfig phase2-cross phase2
PHONY += phase3-validate phase3-abi phase3-interop phase3
PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff phase4-test-fsmount-survey phase4-kprobe-example-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4
PHONY += phase5-validate phase5-test phase5
PHONY += phase6-validate phase6-test phase6-perf phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-perf phase6
PHONY += phase7-validate phase7-test phase7
PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8
PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-loader-commit-alignment-survey phase9-non-owner-boundary-survey phase9-module-metadata-survey phase9-kretprobe-survey phase9-trace-events-survey phase9
PHONY += phase10-validate phase10-test phase10
PHONY += phase11-validate phase11-test phase11-hvc-survey phase11
PHONY += phase12-validate phase12-test phase12
PHONY += phase13-validate phase13-test phase13
PHONY += phase14-validate phase14-smoke phase14-test phase14
PHONY += phase15-validate phase15-test phase15

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase1-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-validation-route-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-validation-route-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py

phase1-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig

phase1-bench:
	cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe

phase1: phase1-validate phase1-test phase1-bench

phase2-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py

phase2-tools:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig

phase2-cross:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py

phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --slug abi --check-build-smoke --zig $(ZIG)
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-validation-flow.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --check-slug-sanity
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test

phase3-abi:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig

phase3-interop:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py

phase3: phase3-validate phase3-abi phase3-interop

phase4-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py

phase4-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-test-fsmount-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig

phase4-kprobe-example-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4: phase4-validate phase4-test

phase5-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase5.py

phase5-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase5_build.zig --summary all

phase5: phase5-validate phase5-test

phase6-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase6.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase6.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-docs-root-external-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-docs-root-external-parity.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py

phase6-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig

phase6-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build perf --build-file zigux/tests/phase6_build.zig

phase6-base64-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build base64-perf --build-file zigux/tests/phase6_build.zig

phase6-bsearch-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build bsearch-perf --build-file zigux/tests/phase6_build.zig

phase6-checksum-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build checksum-perf --build-file zigux/tests/phase6_build.zig

phase6-hexdump-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build hexdump-perf --build-file zigux/tests/phase6_build.zig

phase6: phase6-validate phase6-test

phase7-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-cmdline-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-cmdline-parity.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py

phase7-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all

phase7: phase7-validate phase7-test

phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-validator-flow.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-validator-flow.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-perf-buffer-poll-gate.py

phase8-exec-cmd-test:
	cd $(ZIGUX_ROOT) && $(ZIG) test tools/lib/subcmd/exec-cmd.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all

phase8-help-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all

phase8-kallsyms-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all

phase8-libbpf-segments-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all

phase8-perf-buffer-poll-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test

phase9-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py

phase9-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig --summary all

phase9-loader-gap-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_gap_survey.zig

phase9-loader-commit-alignment-survey:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py

phase9-non-owner-boundary-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_non_owner_boundary_survey.zig

phase9-module-metadata-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig

phase9-kretprobe-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig

phase9-trace-events-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig

phase9: phase9-validate phase9-test

phase10-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-closure-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-closure-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py

phase10-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase10: phase10-validate phase10-test

phase11-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py

phase11-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all

phase11-hvc-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all

phase11: phase11-validate phase11-test phase11-hvc-survey

phase12-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-build-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-build-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-snapshot.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-focused-replay.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-validate phase12-test

phase13-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-libfs-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-libfs-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py

phase13-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase13_build.zig --summary all

phase13: phase13-validate phase13-test

phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py

phase14-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all

phase14-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all

phase14: phase14-validate phase14-test

phase15-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py

phase15-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig

phase15: phase15-validate phase15-test
