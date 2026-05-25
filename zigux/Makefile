PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
PHASE8_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..
PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json
ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["channel"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)
ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["upgrade_policy"]["archive_target_scope"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)
ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)
ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))
ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)
PHONY += phase3-low-level-wrappers-test phase3-policy-starter-packet-test phase3-policy-dump phase3-test phase3-dump phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-trace-events-test phase9-first-loadable-runtime-module-parity-test phase9-test phase11-validate

.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate phase3 phase3-test phase3-dump phase3-policy-dump phase3-export-uapi-layout phase3-low-level-wrappers phase3-export-uapi-layout-test phase3-low-level-wrappers-test phase3-policy-starter-packet-test phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase6-validate phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-bsearch-perf phase6-checksum-test phase6-checksum-perf-matrix-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-test phase6-hexdump-perf phase6-perf phase7-validate phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-trace-events-test phase9-first-loadable-runtime-module-parity-test phase9-test phase10-validate phase10-test phase10 phase11-validate phase12-validate phase12-smoke phase12-test phase12 phase14-validate

phase1-route-summary:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py

phase2-toolchain:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py

phase2-tools:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py

phase2-cross:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py

phase2-genksyms:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py

phase2-fixdep:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-archive-contract-packet.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-closure-archive-contract.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-root-summary.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate
