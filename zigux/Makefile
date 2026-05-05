PHONY += phase1-validate phase1-test phase1-bench phase1
PHONY += phase2-validate phase2-tools phase2-kconfig phase2-cross phase2
PHONY += phase3-validate phase3-abi phase3-interop phase3
PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-bitmap-diff phase4-perf-baseline-survey phase4
PHONY += phase6-test phase6
PHONY += phase7-validate phase7-test phase7
PHONY += phase8-test phase8
PHONY += phase9-test phase9
PHONY += phase10-test phase10
PHONY += phase11-test phase11
PHONY += phase12-test phase12
PHONY += phase13-test phase13
PHONY += phase14-validate phase14-smoke phase14-test phase14
PHONY += phase15-test phase15

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase1-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py

phase1-test:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig

phase1-bench:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py
	cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig

phase1: phase1-validate phase1-test phase1-bench

phase2-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py

phase2-tools:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig

phase2-cross:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py

phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_check_lib.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py --self-test

phase3-abi:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig

phase3-interop:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py

phase3: phase3-validate phase3-abi phase3-interop

phase4-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py

phase4-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4: phase4-validate phase4-test

phase6-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig

phase6: phase6-test

phase7-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py

phase7-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig

phase7: phase7-validate phase7-test

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig

phase8: phase8-test

phase9-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig

phase9: phase9-test

phase10-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig

phase10: phase10-test

phase11-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_build.zig

phase11: phase11-test

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig

phase12: phase12-test

phase13-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase13_build.zig

phase13: phase13-test

phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py

phase14-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all

phase14-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase14_build.zig

phase14: phase14-validate phase14-smoke phase14-test

phase15-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig

phase15: phase15-test
