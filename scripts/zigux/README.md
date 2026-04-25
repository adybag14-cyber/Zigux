# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- committed parity fixture generation and checking
- future ABI/layout guards
- artifact diff helpers for host-side tools

Current bootstrap helpers
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-cross.py`
- `check-mk-elfconfig-diff.py`

Phase 3 flow
- `phase3_catalog.py` discovers Phase 3 slices from the docs, parity wrappers, dump entrypoints, and fixture manifests instead of maintaining one giant hard-coded inventory.
- `phase3_check_lib.py` holds the shared Phase 3 parity execution logic used by every wrapper.
- `generate-phase3-check-wrappers.py` regenerates the tiny `check-phase3-*.py` wrapper stubs from one shared template.
- `validate-phase3.py` validates every discovered slice, its selected manifest, and the required documentation markers.
- `run-phase3-checks.py` lists or executes every discovered `check-phase3-*.py` wrapper through one shared entrypoint.

Rules
- keep helpers narrow and product-facing
- do not duplicate general Linux scripts here
- if a helper becomes broadly useful, move it or integrate it with the native subsystem flow
