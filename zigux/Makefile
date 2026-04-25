PHONY += phase2-validate phase2-tools phase2-kconfig phase2-cross phase2
PHONY += phase3-validate phase3-abi phase3-interop phase3
PHONY += phase6-test phase6
PHONY += phase7-test phase7
PHONY += phase8-test phase8

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase2-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py

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

phase6-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig

phase6: phase6-test

phase7-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig

phase7: phase7-test

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig

phase8: phase8-test
