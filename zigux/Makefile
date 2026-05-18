PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

.PHONY: phase2-validate phase2-toolchain phase2-fixdep phase2-tools phase2-kconfig phase2-cross phase2

phase2-toolchain:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py --zig "$(ZIG)"
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py

phase2-fixdep: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-tools: phase2-fixdep
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py

phase2-kconfig: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig

phase2-validate: phase2-tools phase2-kconfig
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py

phase2-cross: phase2-toolchain
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py

phase2: phase2-validate phase2-cross
