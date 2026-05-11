PHONY += phase1-validate phase1-test phase1-bench phase1
PHONY += phase2-validate phase2-toolchain phase2-cross phase2
PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3
PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4
PHONY += phase5-test phase5
PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6
PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7-test phase7
PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-cpu-mask-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8
PHONY += phase9-runtime-atomic64-test phase9-runtime-bitmap-top-bit-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-runtime-loader-shared-tests phase9-test phase9
PHONY += phase10-validate phase10-test phase10
PHONY += phase11-contract phase11-test phase11-hvc-survey phase11
PHONY += phase12-smoke
PHONY += phase12-test phase12
PHONY += phase13-validate phase13-test phase13
PHONY += phase14-validate phase14-smoke phase14-test phase14
PHONY += phase15-validate phase15-test phase15

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase1-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py

phase1-test:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig

phase1-bench:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py
	cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig

phase1: phase1-validate phase1-test phase1-bench

phase2-toolchain:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py

phase2-validate: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py

phase2-cross: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py

phase2: phase2-validate phase2-cross
