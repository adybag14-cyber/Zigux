PYTHON ?= python3
ZIG ?= zig
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
PHASE8_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..
PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4 phase6-validate phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-checksum-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-test phase6-hexdump-perf phase8-validate phase8-exec-cmd-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12

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
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py

phase3: phase3-validate

phase3-export-uapi-layout-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig

phase4-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py

phase4-artifact-diff-contract:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py

phase4-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-live-helper-replay:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig

phase4-test-fsmount-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig

phase4-kprobe-example-survey:
	cd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig

phase4: phase4-validate phase4-test

phase6-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase6.py

phase6-base64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-base64-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-bsearch-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-review:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-route.py

phase6-hexdump-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig --summary all

phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py

phase8-exec-cmd-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all

phase8-libbpf-segments-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all

phase8-file-path-handle-bridge-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all

phase8-perf-buffer-poll-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase10-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-bootstrap-route.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-shared-freeze-boundary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py

phase10-test:
	cd $(ZIGUX_ROOT) && zig build test --build-file zigux/tests/phase10_build.zig --summary all

phase10: phase10-validate phase10-test

phase12-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-smoke phase12-test
