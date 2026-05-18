PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

.PHONY: phase2-validate phase2-toolchain phase2-fixdep phase2-tools phase2-kconfig phase2

phase2-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py

phase2-toolchain: phase2-validate

phase2-fixdep: phase2-validate
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-tools: phase2-fixdep

phase2-kconfig: phase2-validate
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig

phase2: phase2-tools phase2-kconfig
