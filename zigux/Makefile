PHONY += phase1-validate phase1-test phase1-bench phase1
PHONY += phase2-validate phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2
PHONY += phase3-validate phase3-selftest phase3-abi phase3-interop phase3
PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-bitmap-diff phase4-bitmap-live-helper-replay phase4
PHONY += phase5-test phase5
PHONY += phase6-validate phase6-test phase6-perf phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6
PHONY += phase7-validate phase7-test phase7
PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test phase8
PHONY += phase9-runtime-atomic64-test phase9-runtime-loader-shared-tests phase9-test phase9
PHONY += phase10-test phase10

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase9-runtime-atomic64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig

phase9-runtime-loader-shared-tests:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig

phase9-test:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-build-only-surface.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig

phase9: phase9-test
