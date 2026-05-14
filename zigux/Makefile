PHONY += phase1-validate phase1-test phase1-bench phase1
PHONY += phase2-validate phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2
PHONY += phase3-validate phase3-selftest phase3-abi phase3-low-level-wrappers-test phase3-interop phase3
PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4
PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6
PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7-test phase7
PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-cpu-mask-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8
PHONY += phase9-runtime-atomic64-test phase9-runtime-bitmap-top-bit-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-runtime-loader-shared-tests phase9-test phase9
PHONY += phase10-validate phase10-test phase10
PHONY += phase11-contract phase11-test phase11-hvc-survey phase11
PHONY += phase12-validate phase12-smoke
PHONY += phase12-test phase12
PHONY += phase13-validate phase13-test phase13
PHONY += phase14-validate phase14-smoke phase14-test phase14
PHONY += phase15-validate phase15-test phase15

PYTHON ?= python3
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG ?= $(if $(ZIG_LOCAL_TOOLCHAIN),$(ZIG_LOCAL_TOOLCHAIN),zig)

phase1-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-direct-owner-markers.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-direct-owner-markers.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py

phase1-test:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig

phase1-bench:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py
	cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig

phase1: phase1-validate phase1-test phase1-bench

phase2-toolchain:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py --zig "$(ZIG)"
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py

phase2-tools: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py

phase2-kconfig: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py

phase2-validate: phase2-tools phase2-kconfig
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py

phase2-cross: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py

phase2: phase2-validate phase2-cross

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-selftest-surface.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-selftest-surface.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-readme-tooling-inventory.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-catalog-selftest.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-byte-guards.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-header-family-survey.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-validator-support-surface.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-abi-bindings-syntax.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/survey-phase3-abi-constant-parity.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test

phase3-selftest:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py

phase3-abi:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig

phase3-low-level-wrappers-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig

phase3-interop:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig

phase3: phase3-validate phase3-abi phase3-low-level-wrappers-test phase3-interop

phase4-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py

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

phase6-bsearch-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig

phase6-hexdump-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig

phase6-hexdump-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig

phase6-hexdump-review:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig

phase7-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py

phase7-string-helpers-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-string-helpers-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-string-helpers-sample-boundary:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-string-helpers-sample-boundary --build-file zigux/tests/phase7_build.zig --summary all

phase7-cmdline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-cmdline-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-argv-split-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-argv-split-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-rbtree-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all

phase7: phase7-validate phase7-test

phase9-runtime-atomic64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-bitmap-top-bit-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-trace-events-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-kretprobe-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-shared-tests:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-trace-events-loader-substrate-drift-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-test:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-build-only-surface.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig --summary all

phase9: phase9-runtime-atomic64-test phase9-runtime-bitmap-top-bit-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-runtime-loader-shared-tests phase9-test

phase10-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-core-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-freeze-boundary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-freeze-boundary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py

phase10-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase10: phase10-validate phase10-test

phase11-contract:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-summary-surfaces.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-summary-surfaces.py

phase11-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all

phase11-hvc-survey:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py
	cd $(ZIGUX_ROOT) && $(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all

phase11: phase11-contract phase11-test phase11-hvc-survey

phase12-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py

phase12-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-validate phase12-smoke phase12-test

phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py

phase14-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all

phase14-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all

phase14: phase14-validate phase14-smoke phase14-test
