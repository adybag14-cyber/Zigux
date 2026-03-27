# zigux/tests

This directory is the future home of reusable Zigux parity and differential validation harnesses.

Initial purpose
- hold shared harness logic before subsystem-specific tests spread through the tree
- keep product-facing validation code separate from ad hoc experiments
- provide the first checks for helper parity, ABI assertions, and rollback readiness

Early priorities
- helper differential tests for `tools/lib/*.zig`
- atomic and bitmap parity harnesses
- artifact-diff scaffolding for build-tool dual implementations

Current entrypoint
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/build.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/fixdep/cases.json`
- `zigux/tests/fixtures/fixdep/sample.d`
- `zigux/tests/fixtures/fixdep/sample_expected.txt`
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`
- `zigux/tests/fixtures/genksyms_crc/inputs.txt`
- `zigux/tests/fixtures/genksyms_crc/expected.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/sample_expected.json`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/mk_elfconfig/cases.json`
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist_manifest.json`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
