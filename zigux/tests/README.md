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
- `zigux/tests/build.zig`
