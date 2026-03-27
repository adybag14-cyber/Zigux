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
- `zigux/tests/build.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/fixdep/cases.json`
- `zigux/tests/fixtures/fixdep/sample.d`
- `zigux/tests/fixtures/fixdep/sample_expected.txt`
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`
- `zigux/tests/fixtures/mk_elfconfig/cases.json`
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json`
