PYTHON ?= python3
ZIG ?= zig
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase7-validate phase7-string-helpers-test phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-test phase7-cmdline-survey phase7-argv-split-test phase7-argv-split-survey phase7-rbtree-test phase7-rbtree-survey phase7-test phase7 phase10-validate phase10-test phase10

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

phase2: phase2-validate

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py

phase3: phase3-validate

phase7-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-cmdline-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-cmdline-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py

phase7-string-helpers-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-string-helpers-test --build-file zigux/tests/phase7_build.zig --summary all

phase7-string-helpers-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-string-helpers-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-string-helpers-sample-boundary:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-string-helpers-sample-boundary --build-file zigux/tests/phase7_build.zig --summary all

phase7-cmdline-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-cmdline-test --build-file zigux/tests/phase7_build.zig --summary all

phase7-cmdline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-cmdline-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-argv-split-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-argv-split-test --build-file zigux/tests/phase7_build.zig --summary all

phase7-argv-split-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-argv-split-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-rbtree-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig --summary all

phase7-rbtree-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig --summary all

phase7-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all

phase7: phase7-validate phase7-test

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
