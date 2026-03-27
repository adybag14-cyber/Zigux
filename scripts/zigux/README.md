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
- `validate-phase1.py`
- `validate-phase2.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-mk-elfconfig-diff.py`
- `fixdep.zig`
- `mk_elfconfig.zig`
- `artifact_diff.py`

Rules
- keep helpers narrow and product-facing
- do not duplicate general Linux scripts here
- if a helper becomes broadly useful, move it or integrate it with the native subsystem flow
