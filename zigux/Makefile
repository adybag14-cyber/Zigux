PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2

phase2-toolchain:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py

phase2-tools:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py

phase2-cross:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py

phase2: phase2-validate
