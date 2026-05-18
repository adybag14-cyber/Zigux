PYTHON ?= python3
ZIG ?= zig
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
PHASE8_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase8-validate phase8-exec-cmd-test phase8-test phase8 phase10-validate phase10-test phase10

phase2-toolchain:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py

phase2-tools:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/confdata_bridge.zig
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py

phase2-cross:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py

phase3: phase3-validate

phase3-export-uapi-layout-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig

phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py

phase8-exec-cmd-test:
	cd $(ZIGUX_ROOT) && $(ZIG) test tools/lib/subcmd/exec-cmd.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase8: phase8-validate phase8-exec-cmd-test phase8-test

phase10-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-bootstrap-route.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py

phase10-test:
	cd $(ZIGUX_ROOT) && zig build test --build-file zigux/tests/phase10_build.zig --summary all

phase10: phase10-validate phase10-test
